import django_tables2 as tables
from django_tables2.utils import A

from ledger.models import Type, Transaction

class TransactionTable(tables.Table):
    ref_num = tables.TemplateColumn(template_name= 'ledger/transaction/partials/in-table-update.html')
    delete = tables.TemplateColumn(template_name= 'ledger/transaction/partials/in-table-delete.html')

    class Meta:
        model = Transaction
        fields = ['source', 'trans_date', 'name', 'amount', 'type']
        sequence = ['ref_num', 'source', 'trans_date', 'name', 'amount', 'type', 'delete']

class TypeTable(tables.Table):
    delete = tables.TemplateColumn(template_name= 'ledger/type/partials/in-table-delete.html')

    class Meta:
        model = Type
        fields = ['name']
        sequence = ['name', 'delete']