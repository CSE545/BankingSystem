from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from user_management.forms import RegistrationForm, LoginForm, EditForm, Transaction_main,Trans_Create
from django.contrib.auth.decorators import login_required


# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    context = {}
    if request.POST:
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                context['inactive'] = True
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
            return redirect('/accounts/profile', context)
    else:
        context = {}
        form = EditForm(instance=request.user)
        context['edit_form'] = form
        return render(request, 'user_management/edit_profile.html', context)


def otp_view(request):
    context = {}
    return render(request, 'user_management/2fa.html', context)


def transaction_main(request):
    trans=Transaction_main(request.POST or None)
    if trans.is_valid():
        trans.save()
        return redirect('../')
    context={
        'trans':trans
    }
    return render(request,'user_management/trans_main.html',context)

def trans_create(request):
    trans_c=Trans_Create(request.POST or None)
    if trans_c.is_valid():
        trans_c.save()
        return redirect('/trans')
    content={
            "trans_c":trans_c
        }
    return render(request,'user_management/trans_create.html',content)
