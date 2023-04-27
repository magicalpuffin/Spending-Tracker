from django import forms

from ledger.models import Type, Transaction

class TypeForm(forms.ModelForm):
    class Meta:
        model= Type
        fields= ['name']

class TransactionForm(forms.ModelForm):
    class Meta:
        model= Transaction
        fields= ['ref_num', 'source', 'name', 'trans_date', 'name', 'amount', 'type']

class UploadTransactionForm(forms.Form):
    source= forms.CharField(max_length=256)
    file = forms.FileField()