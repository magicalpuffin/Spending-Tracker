from django.views.generic import View, TemplateView

from ledger.models import Transaction

class IndexView(TemplateView):
    '''
    '''
    template_name = 'ledger/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = Transaction.objects.all()

        return context
    
# TODO
# Create some sort of report view, plotly, not sure how to best display