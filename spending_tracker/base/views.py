from django.shortcuts import render, redirect
from django.views.generic import TemplateView

# Create your views here.

class IndexView(TemplateView):
    '''
    '''
    template_name = 'base/index.html'

def load_messages(request):
    return render(request, 'base/partials/messages.html')