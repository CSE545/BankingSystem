from account_management.models import Account
from django import forms
from transaction_management.models import FundTransfers, Transaction, CashierCheck
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
                    phone_number=self.cleaned_data.get('to_phone')).primary_account.account_id == from_account_id.account_id:
                self._errors['to_phone'] = self.error_class([
                    "Cannot transfer to the same account. Please change your primary account or use account number to transfer."])
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("from_account", "to_phone", "amount", "status")
        widgets = {'status': forms.HiddenInput()}

class FundRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FundRequestForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['from_account'].error_messages['invalid_choice'] = "Enter a valid Account ID"

    def clean(self):
        super(FundRequestForm, self).clean()
        to_account_id = self.cleaned_data.get('to_account')
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if 'from_account' in self.cleaned_data:
            from_account_id = self.cleaned_data.get('from_account')
            if from_account_id.account_id == to_account_id.account_id:
                self._errors['from_account'] = self.error_class(['Cannot request from the same account'])
            if Account.objects.get(account_id=from_account_id.account_id).account_type == "CREDIT":
                self._errors['from_account'] = self.error_class(['Cannot request from a credit account'])
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("to_account", "from_account", "amount", "status", "is_request")
        widgets = {'status': forms.HiddenInput(), 'from_account': forms.TextInput(), 'is_request': forms.HiddenInput()}


class FundRequestFormEmail(forms.ModelForm):
    from_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(FundRequestFormEmail, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        super(FundRequestFormEmail, self).clean()
        to_account_id = self.cleaned_data.get('to_account')
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if 'from_email' in self.cleaned_data:
            if not User.objects.filter(email=self.cleaned_data.get('from_email')).exists():
                self._errors['from_email'] = self.error_class(['Enter a valid user email'])
            elif User.objects.get(email=self.cleaned_data.get('from_email')).primary_account is None:
                self._errors['from_email'] = self.error_class(["There's no primary account set for the email entered"])
            elif User.objects.get(
                    email=self.cleaned_data.get('from_email')).primary_account.account_id == to_account_id.account_id:
                self._errors['from_email'] = self.error_class([
                    "Cannot transfer from the same account. Please change your primary account or use account number to transfer."])
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("to_account", "from_email", "amount", "status", "is_request")
        widgets = {'status': forms.HiddenInput(), 'is_request': forms.HiddenInput()}


class FundRequestFormPhone(forms.ModelForm):
    from_phone = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(FundRequestFormPhone, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        super(FundRequestFormPhone, self).clean()
        to_account_id = self.cleaned_data.get('to_account')
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if 'from_phone' in self.cleaned_data:
            if not User.objects.filter(phone_number=self.cleaned_data.get('from_phone')).exists():
                self._errors['from_phone'] = self.error_class(['Enter a valid user phone number'])
            elif User.objects.get(phone_number=self.cleaned_data.get('from_phone')).primary_account is None:
                self._errors['from_phone'] = self.error_class(
                    ["There's no primary account set for the phone number entered"])
            elif User.objects.get(
                    phone_number=self.cleaned_data.get('from_phone')).primary_account.account_id == to_account_id.account_id:
                self._errors['from_phone'] = self.error_class([
                    "Cannot transfer from the same account. Please change your primary account or use account number to transfer."])
        return self.cleaned_data

    class Meta:
        model = FundTransfers
        fields = ("to_account", "from_phone", "amount", "status", "is_request")
        widgets = {'status': forms.HiddenInput(), 'is_request': forms.HiddenInput()}


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

class CashierCheckForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CashierCheckForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        super(CashierCheckForm, self).clean()
        from_account_id = self.cleaned_data.get('from_account')
        amount = self.cleaned_data.get('amount')
        balance = Account.objects.get(account_id=from_account_id.account_id).account_balance
        if amount <= 0:
            self._errors['amount'] = self.error_class(['Invalid amount'])
        if amount > balance:
            self._errors['amount'] = self.error_class([
                'Insufficient funds'])
        return self.cleaned_data

    class Meta:
        model = CashierCheck
        fields = ("from_account", "pay_to_the_order_of", "amount", "status")
        widgets = {'status': forms.HiddenInput(), 'pay_to_the_order_of': forms.TextInput()}
