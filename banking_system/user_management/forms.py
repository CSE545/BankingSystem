from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_management.models import User

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
    gender = forms.ChoiceField(choices = GENDER)
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1",
                  "password2","phone_number", "gender")
        