from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict

from django_tables2 import RequestConfig
from django_htmx.http import trigger_client_event
from django.views.generic import View, TemplateView

@method_decorator(login_required, name='dispatch')
class IndexTableMixin(TemplateView):
    '''
    Mixin for an index view with a table and form
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
        
        context['table'] = self.table_class(self.model_class.objects.filter(creator= self.request.user))
        RequestConfig(self.request, paginate= self.table_pagination).configure(context['table'])
        
        context['form'] = self.form_class(request= self.request)

        # Sets the query string
        context['page'] = self.request.GET.get("page", '')
        context['sort'] = self.request.GET.get("sort", '')

        return context
    

class LoadTableMixin(View):
    '''
    Mixin to load a table when requested
    '''
    template_name= None
    table_class= None
    model_class= None
    table_pagination= {
        'per_page': 10
    }

    def get(self, request, *args, **kwargs):
        context= {}
        
        # Uses page and sort in query string when loading the table
        table= self.table_class(self.model_class.objects.filter(creator= self.request.user))
        RequestConfig(request, paginate= self.table_pagination).configure(table)
        context['table'] = table

        return render(request, self.template_name, context)

class CreateMixin(View):
    '''
    Mixin for handling creation post request
    '''
    template_name= None
    form_class= None
    model_class= None
    load_table_trigger: str = None
    load_messages_trigger: str = None

    def post(self, request, *args, **kwargs):
        context= {}

        form= self.form_class(request.POST, request= request)
        context['form'] = form

        # By default, return the form
        response = render(request, self.template_name, context)

        if not form.is_valid():
            return response

        # Adds current user before saving
        new_model = form.save(commit= False)
        new_model.creator= request.user
        new_model.save()

        messages.add_message(request, messages.SUCCESS, f'Created {new_model.name}')

        form= self.form_class(request= request)
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
        # Deletes by primary key and if user is correct
        remove_model = self.model_class.objects.get(pk = pk, creator= request.user)
        remove_model.delete()

        messages.add_message(request, messages.SUCCESS, f'Deleted {remove_model.name}')

        # Adds triggers to response header
        response= HttpResponse('')
        trigger_client_event(response, self.load_table_trigger, {})
        trigger_client_event(response, self.load_messages_trigger, {})

        return response

class UpdateMixin(View):
    '''
    Mixing for updating model, get to initialize form and post to edit model
    '''
    template_name= None
    form_template_name= None
    form_class= None
    model_class= None
    load_table_trigger: str = None
    load_messages_trigger: str = None

    def get(self, request, pk, *args, **kwargs):
        '''
        Designed to return entire modal, uses object to set url in modal
        '''
        context= {}

        model = self.model_class.objects.get(pk = pk)
        form = self.form_class(instance= model, request= request)
        
        context['object'] = model
        context['form'] = form

        return render(request, self.template_name, context)
    
    def put(self, request, pk, *args, **kwargs):
        '''
        Designed to return just the contents within the form
        '''
        context= {}

        model = self.model_class.objects.get(pk = pk)
        data = QueryDict(request.body).dict()
        form = self.form_class(data, instance= model, request= request)

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