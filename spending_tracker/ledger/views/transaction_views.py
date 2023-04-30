from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import QueryDict
from django.views.generic import View, TemplateView

from django_tables2 import RequestConfig
from django_htmx.http import trigger_client_event

from ledger.models import Transaction, Type
from ledger.forms import TransactionForm, UploadTransactionForm
from ledger.tables import TransactionTable
from ledger.views.singlepageapp_mixin import IndexTableMixin, LoadTableMixin, CreateMixin, DeleteMixin, UpdateMixin

import pandas as pd

# Create your views here.

# TODO
# Have some form of bulk editing

class TransactionIndexView(IndexTableMixin):
    '''
    Displays entire transaction table, sets up modals
    '''
    template_name = 'ledger/transaction/index.html'
    form_class= TransactionForm
    table_class= TransactionTable
    model_class= Transaction
    table_pagination= {
        'per_page': 10
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['uploadform'] = UploadTransactionForm()

        return context

class LoadTransactionTableView(LoadTableMixin):
    '''
    '''
    template_name= 'ledger/transaction/partials/table/table.html'
    table_class= TransactionTable
    model_class= Transaction
    table_pagination= {
        'per_page': 10
    }

class TransactionCreateView(CreateMixin):
    '''
    '''
    template_name= 'ledger/transaction/partials/create/form.html'
    form_class= TransactionForm
    table_class= TransactionTable
    model_class= Transaction
    load_table_trigger = 'loadTransactionTable'
    load_messages_trigger = 'loadMessages'

class TransactionDeleteView(DeleteMixin):
    model_class= Transaction
    load_table_trigger = 'loadTransactionTable'
    load_messages_trigger = 'loadMessages'

class TransactionUpdateView(UpdateMixin):
    template_name= 'ledger/transaction/partials/update/modal.html'
    form_template_name= 'ledger/transaction/partials/update/form.html'
    form_class= TransactionForm
    model_class= Transaction
    load_table_trigger = 'loadTransactionTable'
    load_messages_trigger = 'loadMessages'

@method_decorator(login_required, name='dispatch')
class TransactionUploadView(View):
    template_name= 'ledger/transaction/partials/upload/form.html'
    form_class= UploadTransactionForm
    model_class= Transaction
    model_type_class= Type

    def post(self, request, *args, **kwargs):
        context= {}

        form= self.form_class(request.POST, request.FILES)
        context['uploadform'] = form
        
        response = render(request, self.template_name, context)

        # If form is not valid, return the form
        if not form.is_valid():
            return response

        upload_file = request.FILES["file"]
        
        # If file is not a csv, give warning
        if not upload_file.name.endswith('.csv'):
            self._handle_csv_error(request, response)
            return response
        
        upload_df = pd.read_csv(upload_file)

        # If columns does not contain key model fields, give warning
        if not set(['ref_num', 'trans_date', 'name', 'amount']).issubset(upload_df.columns):
            self._handle_column_error(request, response)
            return response
        
        # Only sets certain columns in item creation
        if set(['ref_num', 'trans_date', 'name', 'amount', 'type']).issubset(upload_df.columns):
            upload_df = upload_df[['ref_num', 'trans_date', 'name', 'amount', 'type']]
        else:
            upload_df = upload_df[['ref_num', 'trans_date', 'name', 'amount']]

        # Filter sout data if ref_num already in databasea
        upload_df = self._remove_duplicates(request, upload_df)

        # If no new transactions are created, give warning
        if len(upload_df) < 1:
            self._handle_no_new_transactions_error(request, response)
            return response
        
        # Saves data, returns failed indexes
        failed_indexs = self._save_transactions(request, upload_df)

        form= self.form_class()
        context['form'] = form
        response = render(request, self.template_name, context)

        self._handle_successful_upload(request, response, upload_df, failed_indexs)
            
        return response
    
    def _handle_csv_error(self, request, response):
        messages.add_message(request, messages.WARNING, f'File is not a csv')
        trigger_client_event(response, 'loadMessages', {})

    def _handle_column_error(self, request, response):
        messages.add_message(request, messages.WARNING, f'Incorrect columns')
        trigger_client_event(response, 'loadMessages', {})

    def _remove_duplicates(self, request, upload_df):
        existing_ref_num = self.model_class.objects.filter(creator= request.user).values_list('ref_num', flat=True)
        duplicate_ref_num = upload_df['ref_num'].isin(existing_ref_num)

        upload_df = upload_df[~duplicate_ref_num]

        if duplicate_ref_num.sum() > 0:
            messages.add_message(request, messages.WARNING, f'Skipping {duplicate_ref_num.sum()} duplicate ref_nums')
        
        return upload_df

    def _handle_no_new_transactions_error(self, request, response):
        messages.add_message(request, messages.WARNING, f'No transactions with new ref_nums')
        trigger_client_event(response, 'loadMessages', {})

    def _save_transactions(self, request, upload_df):
        failed_indexs = []
        for index, row in upload_df.iterrows():
            data_dict = row.to_dict()

            data_dict['type'] = None
            # If data has a type column, try to match it by name
            if 'type' in row.index:
                data_dict['type'] = self.model_type_class.objects.filter(creator= request.user, name= row['type']).first()
            
            # If there is no type column or match fails, try to use a similar transaction's type
            if data_dict['type'] == None:
                similar_transaction = self.model_class.objects.filter(creator= request.user, name= row['name']).first()
                if similar_transaction:
                    data_dict['type'] = similar_transaction.type

            data_dict['source'] = request.POST.get('source')

            form = TransactionForm(data_dict)
            if form.is_valid():
                new_model = form.save(commit= False)
                new_model.creator = request.user
                new_model.save()
            else:
                failed_indexs.append(index)
        
        if failed_indexs:
            messages.add_message(request, messages.WARNING, f'Unable to add {failed_indexs}')
        
        return failed_indexs

    def _handle_successful_upload(self, request, response, upload_df, failed_indexs):
        messages.add_message(request, messages.SUCCESS, f'Added {len(upload_df) - len(failed_indexs)} transactions')
        trigger_client_event(response, 'loadTransactionTable', {})
        trigger_client_event(response, 'loadMessages', {})