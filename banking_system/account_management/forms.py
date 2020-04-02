from django import forms
from account_management.models import AccountRequests
from user_management.models import User
from django.forms import DateTimeInput


class BootstrapDateTimePickerInput(DateTimeInput):
    template_name = 'widgets/bootstrap_datetimepicker.html'

    def get_context(self, name, value, attrs):
        datetimepicker_id = 'datetimepicker_{name}'.format(name=name)
        if attrs is None:
            attrs = dict()
        attrs['data-target'] = '#{id}'.format(id=datetimepicker_id)
        attrs['class'] = 'form-control datetimepicker-input'
        context = super().get_context(name, value, attrs)
        context['widget']['datetimepicker_id'] = datetimepicker_id
        return context


class BankAccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = AccountRequests
        fields = ('account_type',)

class CustomerAccountForm(forms.Form):
    """ This form is used by tier 2 employee to create new customer bank account."""
    customer = forms.ModelChoiceField(queryset=User.objects.filter(user_type='CUSTOMER'), empty_label=" ")
    ACCOUNT_Types = [('CHECKING', 'Checking'), ('SAVINGS', 'Savings'), ('CREDIT', 'Credit')]
    account_type = forms.CharField(label='Account type', widget=forms.Select(choices=ACCOUNT_Types))

class StatementRequestForm(forms.Form):
    start_date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )
