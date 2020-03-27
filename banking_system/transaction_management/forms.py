from account_management.models import Account
from django import forms
from transaction_management.models import FundTransfers, Transaction
from user_management.models import User


class FundTransferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FundTransferForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['to_account'].error_messages['invalid_choice'] = "Enter a valid Account ID"

    def clean(self):
        super(FundTransferForm, self).clean()
        from_account_id = self.cleaned_data.get('from_account')
        amount = self.cleaned_data.get('amount')
        balance = Account.objects.get(account_id=from_account_id.account_id).account_balance
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if amount > balance:
            self._errors['amount'] = self.error_class([
                'Insufficient funds'])
        if 'to_account' in self.cleaned_data:
            to_account_id = self.cleaned_data.get('to_account')
            if from_account_id.account_id == to_account_id.account_id:
                self._errors['to_account'] = self.error_class(['Cannot transfer to the same account'])
            if Account.objects.get(account_id=to_account_id.account_id).account_type == "CREDIT":
                self._errors['to_account'] = self.error_class(['Cannot transfer to a credit account'])
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("from_account", "to_account", "amount", "status")
        widgets = {'status': forms.HiddenInput(), 'to_account': forms.TextInput()}


class FundTransferFormEmail(forms.ModelForm):
    to_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(FundTransferFormEmail, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        super(FundTransferFormEmail, self).clean()
        from_account_id = self.cleaned_data.get('from_account')
        amount = self.cleaned_data.get('amount')
        balance = Account.objects.get(account_id=from_account_id.account_id).account_balance
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if amount > balance:
            self._errors['amount'] = self.error_class([
                'Insufficient funds'])
        if 'to_email' in self.cleaned_data:
            if not User.objects.filter(email=self.cleaned_data.get('to_email')).exists():
                self._errors['to_email'] = self.error_class(['Enter a valid user email'])
            elif User.objects.get(email=self.cleaned_data.get('to_email')).primary_account is None:
                self._errors['to_email'] = self.error_class(["There's no primary account set for the email entered"])
            elif User.objects.get(
                    email=self.cleaned_data.get('to_email')).primary_account.account_id == from_account_id.account_id:
                self._errors['to_email'] = self.error_class([
                    "Cannot transfer to the same account. Please change your primary account or use account number to transfer."])
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("from_account", "to_email", "amount", "status")
        widgets = {'status': forms.HiddenInput()}


class FundTransferFormPhone(forms.ModelForm):
    to_phone = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(FundTransferFormPhone, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        super(FundTransferFormPhone, self).clean()
        from_account_id = self.cleaned_data.get('from_account')
        amount = self.cleaned_data.get('amount')
        balance = Account.objects.get(account_id=from_account_id.account_id).account_balance
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if amount > balance:
            self._errors['amount'] = self.error_class([
                'Insufficient funds'])
        if 'to_phone' in self.cleaned_data:
            if not User.objects.filter(phone_number=self.cleaned_data.get('to_phone')).exists():
                self._errors['to_phone'] = self.error_class(['Enter a valid user phone number'])
            elif User.objects.get(phone_number=self.cleaned_data.get('to_phone')).primary_account is None:
                self._errors['to_phone'] = self.error_class(
                    ["There's no primary account set for the phone number entered"])
            elif User.objects.get(
                    phone=self.cleaned_data.get('to_phone')).primary_account.account_id == from_account_id.account_id:
                self._errors['to_phone'] = self.error_class([
                    "Cannot transfer to the same account. Please change your primary account or use account number to transfer."])
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("from_account", "to_phone", "amount", "status")
        widgets = {'status': forms.HiddenInput()}


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['to_account'].error_messages['invalid_choice'] = "Enter a valid Account ID"

    def clean(self):
        super(TransactionForm, self).clean()
        from_account_id = self.cleaned_data.get('from_account')
        amount = self.cleaned_data.get('amount')
        balance = Account.objects.get(account_id=from_account_id.account_id).account_balance
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if amount > balance:
            self._errors['amount'] = self.error_class(['Insufficient funds'])
        if 'to_account' in self.cleaned_data:
            to_account_id = self.cleaned_data.get('to_account')
            if from_account_id.account_id == to_account_id.account_id:
                self._errors['to_account'] = self.error_class(['Cannot transfer to the same account'])
            if Account.objects.get(account_id=to_account_id.account_id).account_type == "CREDIT":
                self._errors['to_account'] = self.error_class(['Cannot transfer to a credit account'])
        return self.cleaned_data

    class Meta:
        model = Transaction
        fields = ("from_account", "to_account", "amount", "status")
        widgets = {'status': forms.HiddenInput(), 'to_account': forms.TextInput()}
