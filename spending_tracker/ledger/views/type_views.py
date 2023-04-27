from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import View, TemplateView

from django_tables2 import RequestConfig
from django_htmx.http import trigger_client_event

from ledger.models import Type
from ledger.forms import TypeForm
from ledger.tables import TypeTable

# Create your views here.

class TypeIndexView(TemplateView):
    '''
    '''
    template_name = 'ledger/type/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['table'] = TypeTable(Type.objects.all())
        RequestConfig(self.request, paginate={"per_page": 10}).configure(context['table'])
        
        context['form'] = TypeForm()

        context['page'] = self.request.GET.get("page", '')
        context['sort'] = self.request.GET.get("sort", '')

        return context

def load_type_table(request):
    '''
    Used to reload the table, should be triggered
    '''
    # Automatically uses the query string to load the correct page of table
    table= TypeTable(Type.objects.all())
    RequestConfig(request, paginate={"per_page": 10}).configure(table)
    
    return render(request, 'ledger/type/partials/table.html', {'table': table})


def type_create(request):
    if request.method == 'POST':
        type_form= TypeForm(request.POST)

        if type_form.is_valid():
            new_type = type_form.save()

            table= TypeTable(Type.objects.all())
            RequestConfig(request, paginate={"per_page": 10}).configure(table)

            messages.add_message(request, messages.SUCCESS, f'Created {new_type.name}')

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

        response= HttpResponse('')
        trigger_client_event(response, 'loadTypeTable', {})
        trigger_client_event(response, 'loadMessages', {})

    return response