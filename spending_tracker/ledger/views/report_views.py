import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View, TemplateView

from ledger.models import Transaction

@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    '''
    '''
    template_name = 'ledger/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = Transaction.objects.filter(creator = self.request.user)

        transaction_queryset= Transaction.objects.filter(creator = self.request.user).values_list('name', 'trans_date', 'amount', 'type__name')
        transaction_df = pd.DataFrame.from_records(list(transaction_queryset), columns= ['name', 'trans_date', 'amount', 'type'])

        fig = go.Figure()
        for type_val in transaction_df['type'].unique():
            type_df = transaction_df[transaction_df['type'] == type_val]
            fig.add_trace(
                go.Histogram(
                    name= type_val,
                    x= type_df['trans_date'],
                    y= type_df['amount'],
                    xbins= dict(size= 'M1'),
                    histfunc= 'sum',
                    texttemplate= "%{y}"
                )
            )
        fig.update_layout(
            title= ("<b>Total Spending Over Time</b><br>" + 
                "<i>Spending by Type</i>"),
            barmode= 'stack',
            bargap = 0.1,
            height = 600
        )
        fig.update_yaxes(
            title_text= "Cost ($)"
        )
        fig.update_xaxes(
            dtick = 'M1',
            ticklabelmode= 'period'
        )

        fig_html = plot(fig, output_type= 'div')
        context['fig_html'] = fig_html

        return context
    
# TODO
# Create some sort of report view, plotly, not sure how to best display