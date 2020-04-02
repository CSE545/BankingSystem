from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from account_management.forms import BankAccountForm, CustomerAccountForm
from django.core.exceptions import PermissionDenied
from account_management.models import AccountRequests, Account, DepositRequest
from user_management.models import User
from account_management.utility.manage_accounts import create_account_for_current_request
from account_management.utility.manage_accounts import create_deposit_request
from account_management.utility.manage_accounts import update_deposit_request, withdraw_money
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

def open_customer_account(request):
    context = {}
    if request.POST:
        form = CustomerAccountForm(request.POST)
        if form.is_valid():
            account_type = form.cleaned_data['account_type']
            customer_info = form.cleaned_data['customer']
            user = User.objects.filter(email=customer_info.email).get()
            new_record = Account(account_type=account_type, user_id=user)
            new_record.save()
            context['account_created'] = True
    else:
        form = CustomerAccountForm()
        context['open_customer_account_form'] = form
    return render(request, 'account_management/open_customer_account.html', context)

@login_required
def view_accounts(request):
    if request.POST:
        User.objects.filter(user_id=request.user.user_id).update(
            primary_account=request.POST['account_num'])
    context = {}
    context['account_details'] = {
        'headers': ['Account number', 'Account type', 'Account balance', 'Action'],
        'accounts': []
    }
    user_accounts = Account.objects.filter(user_id=request.user)
    primary_account = User.objects.get(
        user_id=request.user.user_id).primary_account
    primary_account_id = primary_account.account_id if primary_account else None
    for acc in user_accounts:
        if acc.account_type == "CREDIT":
            primary_account_flag = -1
        elif acc.account_id == primary_account_id:
            primary_account_flag = 1
        else:
            primary_account_flag = 0
        context['account_details']['accounts'].append([
            acc.account_id,
            acc.account_type,
            acc.account_balance,
            primary_account_flag
        ])
    return render(request, 'account_management/view_accounts.html', context)

# Tier 2 employees accessing customer accounts
@login_required
def view_customer_accounts(request):
    context = {}
    if request.POST:
        print(request.POST['operation_type'])
        account_number = int(request.POST['account_number'])
        if request.POST['operation_type'] == 'DELETE':
            # account_number = int(request.POST['account_number'])
            print("account number", request.POST['account_number'])
            # Checking if the selected account is the primary account of the customer
            results = User.objects.filter(primary_account_id=account_number)
            if results.count() > 0:
                print("This account is the customer's primary account!")
                for result in results:
                    user_id = result.user_id
                    print("user_id", user_id)
                print("Finding if user have another account that can be made the primary account")  
                customer_accounts = Account.objects.filter(user_id=user_id)
                found = False
                for acc in customer_accounts:
                    if acc.account_id != account_number:
                        print(acc.account_id)
                        if acc.account_type == 'CREDIT':
                            continue

                        user = User.objects.get(user_id=user_id)
                        print("user primary account ", user.primary_account_id)
                        user.primary_account_id = acc.account_id
                        user.save()
                        found = True
                        break
                    else:
                        print("account id equal to selected account!")
                if not found:
                    print("The customer doesn't have another account that" +
                          " can be made the primary account")
                    return render(request, 'customer_account_deletion_failed.html')
                else:
                    Account.objects.filter(account_id=account_number).delete()
        elif request.POST['operation_type'] == 'MODIFY':
            print("in Modify", account_number)
            account_details = Account.objects.get(account_id=account_number)
            print(account_details)
            context['is_modify_clicked'] = True
            context['user_accounts'] = {
            'headers': ['Account number', 'Account type', 'Account balance'],
            'details': {
                'account_balance': account_details.account_balance,
                'account_number': account_details.account_id,
                'account_type': account_details.account_type,
            }
            }
    else:
        customer_bank_accounts = Account.objects.filter()
        context['account_details'] = {
            'headers': ['Account number', 'Account type', 'Account balance', 'Action'],
            'accounts': []
        }
        for acc in customer_bank_accounts:
            context['account_details']['accounts'].append([
                acc.account_id,
                acc.account_type,
                acc.account_balance
            ])
    return render(request, 'account_management/view_customer_bank_accounts.html', context)

def create_customer_account(request):
    #Find customers from all of the users
    customers = User.objects.filter(user_type='CUSTOMER').values('user_id', 'email', 'first_name', 'last_name')



@login_required
def view_requests(request):
    if request.user.user_type != 'T2':
        raise PermissionDenied()
    context = {}
    if request.POST:
        if request.POST['status'] == 'APPROVE':
            user = User.objects.get(email=request.POST['email'])
            account = create_account_for_current_request(
                user, request.POST['account_type'])
            AccountRequests.objects.filter(user_id=user).update(
                status='APPROVED'
            )
            if user.primary_account is None and account.account_type != "CREDIT":
                User.objects.filter(email=request.POST['email']).update(
                    primary_account=account
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


@login_required
def deposit(request, pk=None):
    context = {}
    if pk and request.POST:
        amount = request.POST['amount']
        account_id = request.POST['account_id']
        deposit_request = create_deposit_request(
            request.user, amount, account_id)
        context['deposit_request_submitted'] = True
        return render(request, 'account_management/deposit.html', context)
    elif pk:
        context['account_selected'] = True
        current_account = Account.objects.get(account_id=pk)
        context['user_accounts'] = {
            'headers': ['Account number', 'Account type', 'Account balance'],
            'details': {
                'account_balance': current_account.account_balance,
                'account_number': current_account.account_id,
                'account_type': current_account.account_type,
            }
        }
        return render(request, 'account_management/deposit.html', context)
    else:
        context['user_accounts'] = {
            'headers': ['Account number', 'Account type', 'Account balance'],
            'details': []
        }
        context['select_account'] = True
        user_accounts = Account.objects.filter(
            user_id=request.user,
            account_type__in=["SAVINGS", "CHECKING"])
        for account in user_accounts:
            context['user_accounts']['details'].append([
                account.account_id,
                account.account_type,
                account.account_balance
            ])
    return render(request, 'account_management/deposit.html', context)


@login_required
def withdraw(request, pk=None):
    context = {}
    if pk and request.POST:
        amount = request.POST['amount']
        account_id = request.POST['account_id']
        if withdraw_money(account_id, amount):
            context['withdraw_successful'] = True
        else:
            context['withdraw_successful'] = False
        return render(request, 'account_management/withdraw.html', context)
    elif pk:
        context['account_selected'] = True
        current_account = Account.objects.get(account_id=pk)
        context['user_accounts'] = {
            'headers': ['Account number', 'Account type', 'Account balance'],
            'details': {
                'account_balance': current_account.account_balance,
                'account_number': current_account.account_id,
                'account_type': current_account.account_type,
            }
        }
        return render(request, 'account_management/withdraw.html', context)
    else:
        context['user_accounts'] = {
            'headers': ['Account number', 'Account type', 'Account balance'],
            'details': []
        }
        context['select_account'] = True
        user_accounts = Account.objects.filter(
            user_id=request.user,
            account_type__in=["SAVINGS", "CHECKING"])
        for account in user_accounts:
            context['user_accounts']['details'].append([
                account.account_id,
                account.account_type,
                account.account_balance
            ])
    return render(request, 'account_management/withdraw.html', context)

# TODO Remove login required annotation with middlewares
@login_required
def customer_deposits(request):
    context = {}
    if request.POST:
        update_deposit_request(
            request.POST['account_id'], request.POST['action'])
    customer_deposits = DepositRequest.objects.filter(status='NEW')
    context['deposits'] = {
        'headers': ['Deposit amount', 'User first name', 'User last name', 'User email id'],
        'details': []
    }
    for deposit in customer_deposits:
        context['deposits']['details'].append([
            deposit.deposit_amount,
            deposit.user_id.first_name,
            deposit.user_id.last_name,
            deposit.user_id.email,
            deposit.deposit_id
        ])
    return render(request, 'account_management/customer_deposit_requests.html', context)
