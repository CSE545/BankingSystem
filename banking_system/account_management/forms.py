from django import forms
from account_management.models import AccountRequests, Account


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    
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

class StatementRequestForm(forms.Form):
        DATEPICKER = {
        'type': 'text',
        'class': 'form-control',
        'id': 'datetimepicker1'
        }
        # Call attrs with form widget
        start_date = forms.DateField(label="Start Date")
        
             