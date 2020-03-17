from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from user_management.forms import RegistrationForm, LoginForm, EditForm
from django.contrib.auth.decorators import login_required
from user_management.models import UserLog, User


# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        create_user_log(user_id=request.user.user_id, log_str="User Already Logged In", log_type="info")
        return redirect('home')
    context = {}
    if request.POST:
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                try:
                    login(request, user)
                    create_user_log(user_id=user.user_id, log_str="Login Successful", log_type="info")
                    return redirect('home')
                except Exception as ex:
                    create_user_log(user_id=user.user_id, log_str="Login Failed", log_type="error")
                    form = LoginForm()
                    context['login_form'] = form
                    return render(request, 'user_management/login.html', context)
            else:
                context['inactive'] = True
                create_user_log(user_id=user.user_id, log_str="Login Failed: User Inactive", log_type="debug")
                form = LoginForm(request, data=request.POST)
                context['login_form'] = form
                return render(request, 'user_management/login.html', context)
        else:
            context['user_none'] = True
            form = LoginForm(request, data=request.POST)
            context['login_form'] = form
            return render(request, 'user_management/login.html', context)
    else:
        form = LoginForm()
        context['login_form'] = form
    return render(request, 'user_management/login.html', context)


def register_view(request):
    context = {}
    context['created'] = False
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(email=email, password=raw_password)
            # login(request, user)
            # return redirect('home')
            context['created'] = True
            create_user_log(user_id=user.user_id, log_str="Register Successful", log_type="info")
        else:
            context['registration_form'] = form
    else:  # GET REQUEST
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'user_management/register.html', context)


def logout_user(request):
    logout(request)
    context = {}
    form = LoginForm()
    context['login_form'] = form
    return redirect(request, 'user_management/login.html')


@login_required
def view_profile(request):
    context = {'user': request.user}
    return render(request, 'user_management/profile.html', context)


@login_required
def edit_profile(request):
    if request.POST:
        form = EditForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            context = {}
            context['request_received'] = True
            print('request_received')
            create_user_log(user_id=request.user.user_id, log_str="Profile Edit Successful", log_type="info")
            return redirect('/accounts/profile', context)
    else:
        context = {}
        form = EditForm(instance=request.user)
        context['edit_form'] = form
        create_user_log(user_id=request.user.user_id, log_str="Profile Edit Failed: Non POST call", log_type="debug")
        return render(request, 'user_management/edit_profile.html', context)


# use this function only in POST calls. Writing in db is not recommended in GET calls.
def create_user_log(user_id, log_str, log_type):
    user_log = UserLog.objects.create(user_id=User.objects.get(user_id=user_id), log=log_str, log_type=log_type)
    user_log.save()
