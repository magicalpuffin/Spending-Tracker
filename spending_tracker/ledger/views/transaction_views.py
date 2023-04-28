from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
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
    template_name= 'ledger/transaction/partials/table.html'
    table_class= TransactionTable
    model_class= Transaction

    def get(self, request, *args, **kwargs):
        # Automatically uses the query string to load the correct page of table
        context= {}
        
        table= self.table_class(self.model_class.objects.all())
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        context['table'] = table

        return render(request, self.template_name, context)


# def load_transaction_table(request):
#     '''
#     Used to reload the table, should be triggered
#     '''
#     # Automatically uses the query string to load the correct page of table
#     table= TransactionTable(Transaction.objects.all())
#     RequestConfig(request, paginate={"per_page": 10}).configure(table)
    
#     return render(request, 'ledger/transaction/partials/table.html', {'table': table})

class TransactionCreateView(View):
    '''
    '''
    template_name= 'ledger/transaction/partials/form.html'
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

            table= self.table_class(self.model_class.objects.all())
            RequestConfig(request, paginate={"per_page": 10}).configure(table)

            messages.add_message(request, messages.SUCCESS, f'Created {new_transaction.name}')

            form= self.form_class()
            context['form'] = form

            response = render(request, self.template_name, context)
            
            # htmx triggers
            trigger_client_event(response, 'loadTransactionTable', {})
            trigger_client_event(response, 'loadMessages', {})

        # Successful returns don't close the modal, would need to jquery or htmx hid the modal
        return response

# def transaction_create(request):
#     if request.method == 'POST':
#         transaction_form= TransactionForm(request.POST)

#         if transaction_form.is_valid():
#             new_transaction = transaction_form.save()

#             table= TransactionTable(Transaction.objects.all())
#             RequestConfig(request, paginate={"per_page": 10}).configure(table)

#             messages.add_message(request, messages.SUCCESS, f'Created {new_transaction.name}')

#             form= TransactionForm()
#             response = render(request, 'ledger/transaction/partials/form.html', {'form': form})
            
#             # htmx triggers
#             trigger_client_event(response, 'loadTransactionTable', {})
#             trigger_client_event(response, 'loadMessages', {})
#         else:
#             # Returns form with errors
#             response = render(request, 'ledger/transaction/partials/form.html', {'form': transaction_form})

#     # Successful returns doesn't close modal, would need to jquery or htmx hid the modal
#     return response

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

# def transaction_delete(request, pk):
#     if request.method == 'DELETE':
#         remove_transaction = Transaction.objects.get(pk = pk)
#         remove_transaction.delete()

#         messages.add_message(request, messages.SUCCESS, f'Deleted {remove_transaction.name}')

#         # Adds triggers to response header
#         response= HttpResponse('')
#         trigger_client_event(response, 'loadTransactionTable', {})
#         trigger_client_event(response, 'loadMessages', {})

#     return response

# TODO
# Create some edit view, ideally can click edit from table, maybe link with modal

class TransactionUploadView(View):
    template_name= 'ledger/transaction/partials/upload-form.html'
    form_class= UploadTransactionForm
    model_class= Transaction

    def post(self, request, *args, **kwargs):
        context= {}

        form= self.form_class(request.POST, request.FILES)
        context['uploadform'] = form
        
        response = render(request, self.template_name, context)

        if form.is_valid():
            upload_file = request.FILES["file"]
            
            if not upload_file.name.endswith('.csv'):                
                messages.add_message(request, messages.WARNING, f'File is not a csv')

                trigger_client_event(response, 'loadMessages', {})
                return response
            
            upload_df = pd.read_csv(upload_file)

            if not set(['ref_num', 'trans_date', 'name', 'amount']).issubset(upload_df.columns):
                messages.add_message(request, messages.WARNING, f'Incorrect columns')

                trigger_client_event(response, 'loadMessages', {})
                return response

            # Only adds if data does not conflict with existing ref_nums
            # TODO
            # Display how many/what rows were added, how many were in conflict
            exisitng_ref_num = self.model_class.objects.values_list('ref_num', flat= True)
            upload_df = upload_df[~upload_df['ref_num'].isin(exisitng_ref_num)]

            # TODO
            # Refresh trigger refresh of table and messages
            for index, row in upload_df.iterrows():
                # Uses the form to validate data before submission
                # Adds source from from form to all rows
                data_dict = row.to_dict()
                data_dict['source'] = request.POST.get('source')
                
                # TODO
                # Make these error messages more useful
                try:
                    form = TransactionForm(data_dict)
                    if form.is_valid():
                        form.save()
                    else:
                        messages.add_message(request, messages.WARNING, f'Could not save transaction')
                except Exception as e:
                    messages.add_message(request, messages.WARNING, f'Could not save transaction')
            
            form= self.form_class()
            context['form'] = form
            response = render(request, self.template_name, context)

            trigger_client_event(response, 'loadTransactionTable', {})
            trigger_client_event(response, 'loadMessages', {})

        # TODO
        # Change or decide how things get displayed, this form can probably just close modal and use messages
        return response


# def transaction_upload(request):
#     '''
#     Processes the data upload, requires col names to match
#     '''
#     if request.method == 'POST':
#         transaction_upload_form= UploadTransactionForm(request.POST, request.FILES)
#         if transaction_upload_form.is_valid():
#             upload_file = request.FILES["file"]
            
#             if not upload_file.name.endswith('.csv'):

#                 transaction_upload_form= UploadTransactionForm()
                
#                 messages.add_message(request, messages.WARNING, f'File is not a csv')

#                 response = render(request, 'ledger/transaction/partials/upload-form.html', {'uploadform': transaction_upload_form})
#                 trigger_client_event(response, 'loadMessages', {})
#                 return response
            
#             upload_df = pd.read_csv(upload_file)

#             # Only adds if data does not conflict with existing ref_nums
#             # TODO
#             # Display how many/what rows were added, how many were in conflict
#             exisitng_ref_num = Transaction.objects.values_list('ref_num', flat= True)
#             upload_df = upload_df[~upload_df['ref_num'].isin(exisitng_ref_num)]

#             # TODO
#             # Refresh trigger refresh of table and messages
#             for index, row in upload_df.iterrows():
#                 # Uses the form to validate data before submission
#                 # Adds source from from form to all rows
#                 data_dict = row.to_dict()
#                 data_dict['source'] = request.POST.get('source')
                
#                 # TODO
#                 # Make these error messages more useful
#                 try:
#                     form = TransactionForm(data_dict)
#                     if form.is_valid():
#                         form.save()
#                     else:
#                         messages.add_message(request, messages.WARNING, f'Could not save transaction')
#                 except Exception as e:
#                     messages.add_message(request, messages.WARNING, f'Could not save transaction')

#     # TODO
#     # Change or decide how things get displayed, this form can probably just close modal and use messages
#     return render(request, 'ledger/transaction/partials/upload-form.html', {'uploadform': transaction_upload_form})