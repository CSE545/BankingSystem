from django import forms
from account_management.models import AccountRequests
from user_management.models import User


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

# This form is used by tier 2 employee to create new customer bank account.
class CustomerAccountForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=User.objects.filter(user_type='CUSTOMER'), empty_label=" ")
    ACCOUNT_Types = [('CHECKING', 'Checking'), ('SAVINGS', 'Savings'), ('CREDIT', 'Credit')]
    account_type = forms.CharField(label='Account type', widget=forms.Select(choices=ACCOUNT_Types))
    

    # def __init__(self, *args, **kwargs):
    #     super(CustomerAccountForm, self).__init__(*args, **kwargs)
    #     self.fields['customers'].choices = [(x.user_id, x.first_name) for x in User.objects.
    #                     filter(user_type='CUSTOMER').values('user_id', 'email', 'first_name', 'last_name')]
