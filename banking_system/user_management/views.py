from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def login_view(request):
    return render(request, 'user_management/login.html')
    
def register_view(request):
    form = UserCreationForm()
    context= {'form': form}
    return render(request, 'user_management/register.html', context)