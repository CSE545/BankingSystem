from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from user_management.forms import RegistrationForm

# Create your views here.
def login_view(request):
    return render(request, 'user_management/login.html')
    
def register_view(request):
    context= {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
        else:
            context['registration_form'] = form
    else: #GET
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'user_management/register.html', context)