from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from banking_system.account_management.models import StatementRequest

class StatementRquestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StatementRquestForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = StatementRequest
        fields = ("user", "start_date", "end_date")
