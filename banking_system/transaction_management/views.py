from account_management.models import Account
from django.contrib.auth.decorators import login_required, user_passes_test
from transaction_management.forms import FundTransferForm, FundTransferFormEmail, FundTransferFormPhone
from user_management.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from transaction_management.models import FundTransfers


# Create your views here.

@login_required
def transfers(request):
    from_accounts = Account.objects.filter(user_id=request.user.user_id)
    if request.POST:
        if request.POST['formId'] == 'ACCOUNT':
            form = FundTransferForm(request.POST)
        elif request.POST['formId'] == 'EMAIL':
            form = FundTransferFormEmail(request.POST)
        elif request.POST['formId'] == 'PHONE':
            form = FundTransferFormPhone(request.POST)
        if form.is_valid():
            s = request.POST.dict()
            if s['formId'] == 'EMAIL':
                s['to_account'] = User.objects.get(email=s['to_email']).primary_account
            elif s['formId'] == 'PHONE':
                s['to_account'] = User.objects.get(phone_number=s['to_phone']).primary_account
            form = FundTransferForm(s, request.user)
            instance = form.save(commit=False)
            instance.transfer_type = s['formId']
            instance.save()
            context = {}
            context['request_received'] = True
            print('request_received')
            return redirect('home')
        else:
            context = {'formId': request.POST['formId']}
            account_form = FundTransferForm()
            email_form = FundTransferFormEmail()
            phone_form = FundTransferFormPhone()
            account_form.fields['from_account'].queryset = from_accounts
            email_form.fields['from_account'].queryset = from_accounts
            phone_form.fields['from_account'].queryset = from_accounts
            form.fields['from_account'].queryset = from_accounts
            context['account_form'] = account_form
            context['email_form'] = email_form
            context['phone_form'] = phone_form
            if request.POST['formId'] == 'ACCOUNT':
                context['account_form'] = form
            elif request.POST['formId'] == 'EMAIL':
                context['email_form'] = form
            elif request.POST['formId'] == 'PHONE':
                context['phone_form'] = form
            return render(request, 'transaction_management/transfers.html', context)

    else:
        context = {'formId': 'ACCOUNT'}
        account_form = FundTransferForm()
        email_form = FundTransferFormEmail()
        phone_form = FundTransferFormPhone()
        account_form.fields['from_account'].queryset = from_accounts
        email_form.fields['from_account'].queryset = from_accounts
        phone_form.fields['from_account'].queryset = from_accounts
        context['account_form'] = account_form
        context['email_form'] = email_form
        context['phone_form'] = phone_form
        return render(request, 'transaction_management/transfers.html', context)


def employee_check(user):
    return user.user_type in ["T1", "T2", "T3"]


@login_required
@user_passes_test(employee_check)
def pendingFundTransfers(request):
    if request.POST:
        context = {"pendingFundTransfersData": {"error": ""}}
        curFundObj = FundTransfers.objects.get(
            request_id=int(request.POST['request_id']))
        if (request.POST['status'] == "APPROVED"):
            curBal = Account.objects.get(
                account_id=curFundObj.from_account_id).account_balance
            if curBal >= curFundObj.amount:
                FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(
                    status=request.POST['status'])
                Account.objects.filter(account_id=curFundObj.from_account_id).update(
                    account_balance=curBal - curFundObj.amount)
                Account.objects.filter(account_id=curFundObj.to_account_id).update(account_balance=Account.objects.get(
                    account_id=curFundObj.to_account_id).account_balance + curFundObj.amount)
            else:
                context["pendingFundTransfersData"]["error"] = "Rejected: Insufficient funds"
                FundTransfers.objects.filter(request_id=int(
                    request.POST['request_id'])).update(status="REJECTED")

        else:
            FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(
                status=request.POST['status'])
        return render(request, 'transaction_management/pendingFundTransfers.html', context)
    else:
        context = {}
        context['pendingFundTransfersData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status', u'Approve', u'Reject'],
            'rows': [],
            'error': ""
        }
        for e in FundTransfers.objects.filter(status="NEW"):
            context['pendingFundTransfersData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
                " " + e.to_account.user_id.last_name,
                e.amount,
                e.status
            ])

        context['actionedFundTransfersData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status'],
            'rows': []
        }
        for e in FundTransfers.objects.filter(~Q(status="NEW")):
            context['actionedFundTransfersData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
                " " + e.to_account.user_id.last_name,
                e.amount,
                e.status
            ])
        return render(request, 'transaction_management/pendingFundTransfers.html', context)
