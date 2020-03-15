from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_management.models import User
from django.shortcuts import redirect, render


@login_required
def homepage(request):
    email = request.user.email
    user = User.objects.get(email=email)
    if user.user_type == 'CUSTOMER':
        return render(request, 'homepage.html')
    else:
        return render(request, 'employee_home.html')
