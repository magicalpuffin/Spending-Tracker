from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import TemplateView

from django_tables2 import RequestConfig
from django_htmx.http import trigger_client_event

from .models import Transaction, Type
from .forms import TransactionForm, TypeForm
from .tables import TransactionTable, TypeTable

# Create your views here.

class IndexView(TemplateView):
    '''
    '''
    template_name = 'ledger/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = Transaction.objects.all()

        return context
    
# class TransactionIndexView(TemplateView):
#     '''
#     '''
#     template_name = 'ledger/transaction/index.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['transactions'] = Transaction.objects.all()
#         context['table'] = TransactionTable(Transaction.objects.all())
#         context['form'] = TransactionForm()

#         return context

# TODO
# Switch to class based views later
def transaction_index(request):
    context={}

    # The initialized the index page, sets the query string for when table is reloaded
    context['table']= TransactionTable(Transaction.objects.all())
    RequestConfig(request, paginate={"per_page": 5}).configure(context['table'])
    
    context['form'] = TransactionForm()
    # Sets the query string
    context['page'] = request.GET.get("page", '')
    context['sort'] = request.GET.get("sort", '')

    return render(request, 'ledger/transaction/index.html', context)

# TODO
# Consider some naming convention of things that are supposed to triggered by events or urls
def transaction_table_load(request):
    '''
    Used to reload the table, should be triggered
    '''
    # Automatically uses the query string to load the correct page of table
    table= TransactionTable(Transaction.objects.all())
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    
    return render(request, 'ledger/transaction/partials/table.html', {'table': table})

def transaction_create(request):
    # TODO
    # Is checking for post is meaningful? Use get or 404?
    if request.method == 'POST':
        transaction_form= TransactionForm(request.POST)

        if transaction_form.is_valid():
            new_transaction = transaction_form.save()

            table= TransactionTable(Transaction.objects.all())
            RequestConfig(request, paginate={"per_page": 5}).configure(table)

            messages.add_message(request, messages.SUCCESS, f'Created {new_transaction.name}')

            form= TransactionForm()
            response = render(request, 'ledger/transaction/partials/form.html', {'form': form})
            
            # htmx triggers
            trigger_client_event(response, 'loadTransactionTable', {})
            trigger_client_event(response, 'loadMessages', {})
        else:
            # Returns form with errors
            response = render(request, 'ledger/transaction/partials/form.html', {'form': transaction_form})

    return response


def transaction_delete(request, pk):
    if request.method == 'DELETE':
        remove_transaction = Transaction.objects.get(pk = pk)
        remove_transaction.delete()

        messages.add_message(request, messages.SUCCESS, f'Deleted {remove_transaction.name}')

        # TODO
        # Check if there is a better than having a empty response with request and triggers
        response= HttpResponse('')
        trigger_client_event(response, 'loadTransactionTable', {})
        trigger_client_event(response, 'loadMessages', {})

    return response


# TODO
# Need to implement all table pagination things in transaction
# class TypeIndexView(TemplateView):
#     '''
#     '''
#     template_name = 'ledger/type/index.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['types'] = Type.objects.all()
#         context['table'] = TypeTable(Type.objects.all())
#         context['form'] = TypeForm()

#         return context

def type_index(request):
    context={}

    # The initialized the index page, sets the query string for when table is reloaded
    context['table']= TypeTable(Type.objects.all())
    RequestConfig(request, paginate={"per_page": 5}).configure(context['table'])
    
    context['form'] = TypeForm()
    # Sets the query string
    context['page'] = request.GET.get("page", '')
    context['sort'] = request.GET.get("sort", '')

    return render(request, 'ledger/type/index.html', context)

def type_table_load(request):
    '''
    Used to reload the table, should be triggered
    '''
    # Automatically uses the query string to load the correct page of table
    table= TypeTable(Type.objects.all())
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    
    return render(request, 'ledger/type/partials/table.html', {'table': table})


def type_create(request):
    # TODO
    # Is checking for post is meaningful? Use get or 404?
    if request.method == 'POST':
        type_form= TypeForm(request.POST)

        if type_form.is_valid():
            new_type = type_form.save()

            table= TypeTable(Type.objects.all())
            RequestConfig(request, paginate={"per_page": 5}).configure(table)

            messages.add_message(request, messages.SUCCESS, f'Created {new_type.name}')

            # TODO
            # Organize this
            form= TypeForm()
            response = render(request, 'ledger/type/partials/form.html', {'form': form})
            
            # htmx triggers
            trigger_client_event(response, 'loadTypeTable', {})
            trigger_client_event(response, 'loadMessages', {})
        else:
            # Returns form with errors
            response = render(request, 'ledger/type/partials/form.html', {'form': type_form})

    return response


def type_delete(request, pk):
    if request.method == 'DELETE':
        remove_type = Type.objects.get(pk = pk)
        remove_type.delete()

        messages.add_message(request, messages.SUCCESS, f'Deleted {remove_type.name}')

        # TODO
        # Check if there is a better than having a empty response with request and triggers
        response= HttpResponse('')
        trigger_client_event(response, 'loadTypeTable', {})
        trigger_client_event(response, 'loadMessages', {})

    return response