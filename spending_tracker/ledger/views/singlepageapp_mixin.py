from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.http import QueryDict

from django_tables2 import RequestConfig
from django_htmx.http import trigger_client_event
from django.views.generic import View, TemplateView

class IndexTableMixin(TemplateView):
    '''
    Displays entire transaction table, sets up modals
    '''
    template_name = None
    form_class= None
    table_class= None
    model_class= None
    table_pagination= {
        'per_page': 10
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['table'] = self.table_class(self.model_class.objects.all())
        RequestConfig(self.request, paginate= self.table_pagination).configure(context['table'])
        
        context['form'] = self.form_class()

        # Sets the query string
        context['page'] = self.request.GET.get("page", '')
        context['sort'] = self.request.GET.get("sort", '')

        return context
    

class LoadTableMixin(View):
    '''
    Used to reload the table, should be triggered
    '''
    template_name= None
    table_class= None
    model_class= None
    table_pagination= {
        'per_page': 10
    }

    def get(self, request, *args, **kwargs):
        # Automatically uses the query string to load the correct page of table
        context= {}
        
        table= self.table_class(self.model_class.objects.all())
        RequestConfig(request, paginate= self.table_pagination).configure(table)
        context['table'] = table

        return render(request, self.template_name, context)

class CreateMixin(View):
    '''
    '''
    template_name= None
    form_class= None
    table_class= None
    model_class= None
    load_table_trigger: str = None
    load_messages_trigger: str = None

    def post(self, request, *args, **kwargs):
        context= {}

        form= self.form_class(request.POST)
        context['form'] = form

        # By default, return the form
        response = render(request, self.template_name, context)

        if not form.is_valid():
            return response

        new_model = form.save()

        messages.add_message(request, messages.SUCCESS, f'Created {new_model.name}')

        form= self.form_class()
        context['form'] = form

        response = render(request, self.template_name, context)
        
        # htmx triggers
        trigger_client_event(response, self.load_table_trigger, {})
        trigger_client_event(response, self.load_messages_trigger, {})

        # Successful returns don't close the modal, would need to jquery or htmx hid the modal
        return response
    
class DeleteMixin(View):
    model_class= None
    load_table_trigger: str = None
    load_messages_trigger: str = None

    def delete(self, request, pk, *args, **kwargs):
        remove_model = self.model_class.objects.get(pk = pk)
        remove_model.delete()

        messages.add_message(request, messages.SUCCESS, f'Deleted {remove_model.name}')

        # Adds triggers to response header
        response= HttpResponse('')
        trigger_client_event(response, self.load_table_trigger, {})
        trigger_client_event(response, self.load_messages_trigger, {})

        return response

class UpdateMixin(View):
    template_name= None
    form_template_name= None
    form_class= None
    model_class= None
    load_table_trigger: str = None
    load_messages_trigger: str = None

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
            trigger_client_event(response, self.load_table_trigger, {})
            trigger_client_event(response, self.load_messages_trigger, {})
        
        # Issues with modal being dismissed even with errors
        return response