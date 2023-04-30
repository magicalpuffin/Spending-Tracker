from django import forms

from ledger.models import Type, Transaction

class TypeForm(forms.ModelForm):
    class Meta:
        model= Type
        fields= ['name']

    def __init__(self, *args, **kwargs):
        # Adds request as a kwarg
        self.request = kwargs.pop("request", None)
        super(TypeForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        # Skips error check if name is unchanged
        if self.instance.name == name:
            return cleaned_data

        # Handle error if user already has type name
        if name and self.request:
            if self.Meta.model.objects.filter(creator= self.request.user, name= name).exists():
                raise forms.ValidationError(f"{name} already exists for this user.")
        
        return cleaned_data


class TransactionForm(forms.ModelForm):
    class Meta:
        model= Transaction
        fields= ['ref_num', 'source', 'name', 'trans_date', 'name', 'amount', 'type']
        widgets = {
            'trans_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        # Adds request as a kwarg
        self.request = kwargs.pop("request", None)

        super(TransactionForm, self).__init__(*args, **kwargs)

        # Sets the available types to be those created by user
        if self.request:
            self.fields['type'].queryset = Type.objects.filter(creator = self.request.user)

    
    def clean(self):
        cleaned_data = super().clean()
        ref_num = cleaned_data.get('ref_num')

        # Skips error check if ref_num is unchanged
        if self.instance.ref_num == ref_num:
            return cleaned_data

        # Handles error if user already has transaction ref_num
        if ref_num and self.request:
            if self.Meta.model.objects.filter(creator= self.request.user, ref_num= ref_num).exists():
                raise forms.ValidationError(f"{ref_num} already exists for this user.")
        
        return cleaned_data        

class UploadTransactionForm(forms.Form):
    source= forms.CharField(max_length=256)
    file = forms.FileField()