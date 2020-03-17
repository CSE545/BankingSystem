from django import forms
#from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from transactions.models import EMP_Transaction, EMP_Transaction_Create

class Transaction_main(forms.ModelForm):
    class Meta:
        model = EMP_Transaction
        fields = {'action'}


class Trans_Create(forms.ModelForm):
    class Meta:
        model = EMP_Transaction_Create
        fields = {
            'name',
            'to',
            'transaction_amount'
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "to": forms.TextInput(attrs={"class": "form-control"}),
            "transaction_amount": forms.NumberInput(attrs={"class": "form-control"})
        }
