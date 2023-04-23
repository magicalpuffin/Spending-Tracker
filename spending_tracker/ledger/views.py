from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .models import Transaction, Type
# from .forms import TransactionForm, TypeForm

# Create your views here.

class IndexView(TemplateView):
    '''
    '''
    template_name = 'ledger/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = Transaction.objects.all()

        return context
    
