from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_management.models import User


@login_required
def homepage(request):
    email = request.user.email
    user = User.objects.get(email=email)
    print(user.user_type)
    if user.user_type == 'CUSTOMER':
        return render(request, 'homepage.html')
    elif user.user_type == 'T3':
        return render(request, 't3_employee_home.html')
    elif user.user_type == 'T2':
        return render(request, 't2_employee_home.html')
    return render(request, 'employee_home.html')
