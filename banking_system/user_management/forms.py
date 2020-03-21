from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from user_management.models import User, UserPendingApproval

GENDER = (
    ("M", "MALE"),
    ("F", "FEMALE"),
    ("O", "OTHER"),
)


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    gender = forms.ChoiceField(choices=GENDER)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1",
                  "password2", "phone_number", "gender")


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = User
        fields = ("email", "password")


class EditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = UserPendingApproval
        fields = ("email", "first_name", "last_name", "phone_number", "gender")