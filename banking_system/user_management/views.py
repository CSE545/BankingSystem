from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from user_management.forms import RegistrationForm, LoginForm, EditForm, FundTransferForm
from django.contrib.auth.decorators import login_required, user_passes_test
from user_management.models import User, FundTransferRequest

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
                form = LoginForm(request, data=request.POST)
                context['login_form'] = form
                is_valid_form = form.is_valid()
                if is_valid_form:
                    login(request, user)
                    return redirect('home')
                else:
                    context['otp_sent'] = True
                    return render(request, 'user_management/login.html', context)
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
    if request.user.user_type == 'CUSTOMER':
        base_template_name = 'homepage.html'
    else:
        base_template_name = 'employee_home.html'
    context = {'user': request.user, 'base_template_name': base_template_name}
    return render(request, 'user_management/profile.html', context)


@login_required
def transfers(request):
    if request.POST:
        form = FundTransferForm(request.POST, request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            context = {}
            context['request_received'] = True
            print('request_received')
            return redirect('home')
    else:
        context = {}
        form = FundTransferForm(instance=request.user)
        form.fields['from_account'].queryset = User.objects.filter(
            user_id=request.user.user_id)
        form.fields['to_account'].queryset = User.objects.exclude(
            user_id=request.user.user_id)
        context['transfer_form'] = form
        return render(request, 'user_management/transfers.html', context)


def employee_check(user):
    return user.user_type in ["T1", "T2", "T3"]


@login_required
@user_passes_test(employee_check)
def pendingFundTransfers(request):
    if request.POST:
        FundTransferRequest.objects.filter(request_id=int(
            request.POST['request_id'])).update(status=request.POST['status'])
        return render(request, 'user_management/pendingFundTransfers.html')
    context = {}
    context['pendingFundTransfersData'] = {
        'headers': [u'transactionId', u'from_name', u'to_name', u'amount', u'status', u'approve', u'reject'],
        'rows': []
    }
    for e in FundTransferRequest.objects.filter(status="NEW"):
        context['pendingFundTransfersData']['rows'].append([e.request_id,
                                                            e.from_account.first_name + " " + e.from_account.last_name,
                                                            e.to_account.first_name + " " + e.to_account.last_name,
                                                            e.amount,
                                                            e.status])
    return render(request, 'user_management/pendingFundTransfers.html', context)


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
