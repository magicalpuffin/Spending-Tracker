import django_tables2 as tables
from django_tables2.utils import A

from ledger.models import Type, Transaction

class TransactionTable(tables.Table):
    edit = tables.TemplateColumn(template_name= 'ledger/transaction/partials/table/in-table-update.html')
    delete = tables.TemplateColumn(template_name= 'ledger/transaction/partials/table/in-table-delete.html')

    class Meta:
        model = Transaction
        fields = ['ref_num', 'source', 'trans_date', 'name', 'amount', 'type']
        sequence = ['ref_num', 'source', 'trans_date', 'name', 'amount', 'type', 'edit', 'delete']

class TypeTable(tables.Table):
    delete = tables.TemplateColumn(template_name= 'ledger/type/partials/in-table-delete.html')

    class Meta:
        model = Type
        fields = ['name']
        sequence = ['name', 'delete']