from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from user_management.models import User, UserPendingApproval
from user_management.utility.twofa import generate_otp, get_user_phone_number, save_otp_in_db  # , send_otp


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
    otp = forms.CharField(required=False, widget=forms.PasswordInput)

    def clean(self):
        otp = generate_otp()
        if '_otp' in self.request.session:
            print(self.request.session['_otp'])
        else:
            print('otp', otp)
        cleaned_data = super().clean()
        user = get_user_phone_number(cleaned_data['username'])
        # Uncomment this once the sns credentials are added in twofa.py file
        # send_otp(otp, user.phone_number)
        if '_otp' in self.request.session:
            if str(self.request.session['_otp']) != str(self.cleaned_data['otp']):
                raise forms.ValidationError("Invalid OTP.")
            del self.request.session['_otp']
        else:
            self.request.session['_otp'] = otp
            save_otp_in_db(otp, user)
            raise forms.ValidationError("Enter OTP you received via text")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = User
        fields = ("email", "password", "otp")


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
