from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import View, TemplateView

from django_tables2 import RequestConfig
from django_htmx.http import trigger_client_event

from ledger.models import Type
from ledger.forms import TypeForm
from ledger.tables import TypeTable
from ledger.views.singlepageapp_mixin import IndexTableMixin, LoadTableMixin, CreateMixin, DeleteMixin, UpdateMixin

# Create your views here.

# TODO
# Could refactor to use mixins with type view

class TypeIndexView(IndexTableMixin):
    '''
    '''
    template_name = 'ledger/type/index.html'
    form_class= TypeForm
    table_class= TypeTable
    model_class= Type
    table_pagination= {
        'per_page': 10
    }

class LoadTypeTableView(LoadTableMixin):
    '''
    '''
    template_name= 'ledger/type/partials/table/table.html'
    table_class= TypeTable
    model_class= Type
    table_pagination= {
        'per_page': 10
    }

class TypeCreateView(CreateMixin):
    '''
    '''
    template_name= 'ledger/type/partials/create/form.html'
    form_class= TypeForm
    table_class= TypeTable
    model_class= Type
    load_table_trigger = 'loadTypeTable'
    load_messages_trigger = 'loadMessages'

class TypeDeleteView(DeleteMixin):
    model_class= Type
    load_table_trigger = 'loadTypeTable'
    load_messages_trigger = 'loadMessages'

class TypeUpdateView(UpdateMixin):
    template_name= 'ledger/type/partials/update/modal.html'
    form_template_name= 'ledger/type/partials/update/form.html'
    form_class= TypeForm
    model_class= Type
    load_table_trigger = 'loadTypeTable'
    load_messages_trigger = 'loadMessages'
