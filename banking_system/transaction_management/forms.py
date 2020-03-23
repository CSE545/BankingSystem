from django import forms
from transaction_management.models import FundTransfers
from account_management.models import Account


class FundTransferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FundTransferForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['to_account'].queryset = Account.objects.all().defer('account_balance')

    def clean(self):

        # data from the form is fetched using super function
        super(FundTransferForm, self).clean()

        # extract the username and text field from the data
        from_account_id = self.cleaned_data.get('from_account')
        amount = self.cleaned_data.get('amount')
        balance = Account.objects.get(account_id=from_account_id.account_id).account_balance

        if amount < 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        # conditions to be met for the username length
        if amount > balance:
            self._errors['amount'] = self.error_class([
                'Insufficient funds'])

        # return any errors if found
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("from_account", "to_account", "amount", "status")
        widgets = {'status': forms.HiddenInput()}
