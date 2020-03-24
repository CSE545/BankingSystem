from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account_management.forms import BankAccountForm
from django.core.exceptions import PermissionDenied
from account_management.models import AccountRequests, Account
from user_management.models import User
from account_management.utility.manage_accounts import create_account_for_current_request
# Create your views here.


@login_required
def open_account(request):
    context = {}
    if request.POST:
        form = BankAccountForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user_id = request.user
            instance.save()
            context['request_received'] = True
    else:
        pending_requests = AccountRequests.objects.filter(
            user_id=request.user,
            status='NEW'
        ).count()
        if pending_requests > 0:
            context['pending_request'] = True
        form = BankAccountForm()
        context['bank_form'] = form
    return render(request, 'account_management/open_account.html', context)


@login_required
def view_accounts(request):
    context = {}
    context['account_details'] = {
        'headers': ['Account number', 'Account type', 'Account balance'],
        'accounts': []
    }
    user_accounts = Account.objects.filter(user_id=request.user)
    for acc in user_accounts:
        context['account_details']['accounts'].append([
            acc.account_id,
            acc.account_type,
            acc.account_balance
        ])
    return render(request, 'account_management/view_accounts.html', context)


@login_required
def view_requests(request):
    if request.user.user_type != 'T2':
        raise PermissionDenied()
    context = {}
    if request.POST:
        if request.POST['status'] == 'APPROVE':
            user = User.objects.get(email=request.POST['email'])
            create_account_for_current_request(
                user, request.POST['account_type'])
            AccountRequests.objects.filter(user_id=user).update(
                status='APPROVED'
            )
    context['account_requests'] = {
        'headers': ['First name', 'Last name', 'Email', 'Account type'],
        'body': []
    }
    pending_requests = AccountRequests.objects.filter(status='NEW')
    for pr in pending_requests:
        context['account_requests']['body'].append([
            pr.user_id.first_name,
            pr.user_id.last_name,
            pr.user_id.email,
            pr.account_type
        ])
    return render(request, 'account_management/view_requests.html', context)
