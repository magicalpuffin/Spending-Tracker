from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.http import QueryDict
from django.views.generic import View, TemplateView

from django_tables2 import RequestConfig
from django_htmx.http import trigger_client_event

from ledger.models import Transaction
from ledger.forms import TransactionForm, UploadTransactionForm
from ledger.tables import TransactionTable

import pandas as pd

# Create your views here.
    
class TransactionIndexView(TemplateView):
    '''
    Displays entire transaction table, sets up modals
    '''
    template_name = 'ledger/transaction/index.html'
    form_class= TransactionForm
    table_class= TransactionTable
    model_class= Transaction

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['table'] = self.table_class(self.model_class.objects.all())
        RequestConfig(self.request, paginate={"per_page": 10}).configure(context['table'])
        
        context['form'] = self.form_class()
        context['uploadform'] = UploadTransactionForm()

        # Sets the query string
        context['page'] = self.request.GET.get("page", '')
        context['sort'] = self.request.GET.get("sort", '')

        return context

class LoadTransactionTableView(View):
    '''
    Used to reload the table, should be triggered
    '''
    template_name= 'ledger/transaction/partials/table/table.html'
    table_class= TransactionTable
    model_class= Transaction

    def get(self, request, *args, **kwargs):
        # Automatically uses the query string to load the correct page of table
        context= {}
        
        table= self.table_class(self.model_class.objects.all())
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        context['table'] = table

        return render(request, self.template_name, context)

class TransactionCreateView(View):
    '''
    '''
    template_name= 'ledger/transaction/partials/create/form.html'
    form_class= TransactionForm
    table_class= TransactionTable
    model_class= Transaction

    def post(self, request, *args, **kwargs):
        context= {}

        form= self.form_class(request.POST)
        context['form'] = form

        # By default, return the form
        response = render(request, self.template_name, context)

        if form.is_valid():
            new_transaction = form.save()

            messages.add_message(request, messages.SUCCESS, f'Created {new_transaction.name}')

            form= self.form_class()
            context['form'] = form

            response = render(request, self.template_name, context)
            
            # htmx triggers
            trigger_client_event(response, 'loadTransactionTable', {})
            trigger_client_event(response, 'loadMessages', {})

        # Successful returns don't close the modal, would need to jquery or htmx hid the modal
        return response


class TransactionDeleteView(View):
    model_class= Transaction

    def delete(self, request, pk, *args, **kwargs):
        remove_transaction = self.model_class.objects.get(pk = pk)
        remove_transaction.delete()

        messages.add_message(request, messages.SUCCESS, f'Deleted {remove_transaction.name}')

        # Adds triggers to response header
        response= HttpResponse('')
        trigger_client_event(response, 'loadTransactionTable', {})
        trigger_client_event(response, 'loadMessages', {})

        return response

class TransactionUpdateView(View):
    template_name= 'ledger/transaction/partials/update/modal.html'
    form_template_name= 'ledger/transaction/partials/update/form.html'
    form_class= TransactionForm
    model_class= Transaction

    def get(self, request, pk, *args, **kwargs):
        context= {}

        model = self.model_class.objects.get(pk = pk)
        form = self.form_class(instance= model)
        
        context['object'] = model
        context['form'] = form

        return render(request, self.template_name, context)
    
    def put(self, request, pk, *args, **kwargs):
        context= {}

        model = self.model_class.objects.get(pk = pk)
        data = QueryDict(request.body).dict()
        form = self.form_class(data, instance= model)

        # I don't think model is needed for this
        context['object'] = model
        context['form'] = form

        # Only updating the form, but modal gets dismissed anyways
        response = render(request, self.form_template_name, context)

        if form.is_valid():
            new_model = form.save()
            messages.add_message(request, messages.SUCCESS, f'Updated {new_model.name}')
            
            # htmx triggers
            trigger_client_event(response, 'loadTransactionTable', {})
            trigger_client_event(response, 'loadMessages', {})
        
        # Issues with modal being dismissed even with errors
        return response

# TODO
# Refactor, split into smaller functions, flip if statement to remove indent
class TransactionUploadView(View):
    template_name= 'ledger/transaction/partials/upload/form.html'
    form_class= UploadTransactionForm
    model_class= Transaction

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
        # TODO
        # Automatic type selection by allowing type column, selecting best existing match for duplicate names
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
        existing_ref_num = self.model_class.objects.values_list('ref_num', flat=True)
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
            data_dict['source'] = request.POST.get('source')

            form = TransactionForm(data_dict)
            if form.is_valid():
                form.save()
            else:
                failed_indexs.append(index)
        
        if failed_indexs:
            messages.add_message(request, messages.WARNING, f'Unable to add {failed_indexs}')
        
        return failed_indexs

    def _handle_successful_upload(self, request, response, upload_df, failed_indexs):
        messages.add_message(request, messages.SUCCESS, f'Added {len(upload_df) - len(failed_indexs)} transactions')
        trigger_client_event(response, 'loadTransactionTable', {})
        trigger_client_event(response, 'loadMessages', {})