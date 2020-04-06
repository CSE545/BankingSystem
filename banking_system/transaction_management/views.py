from account_management.models import Account
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render
from transaction_management.forms import FundTransferForm, FundTransferFormEmail, FundTransferFormPhone, \
    TransactionForm, CashierCheckForm, FundRequestForm, FundRequestFormEmail, FundRequestFormPhone
from transaction_management.models import FundTransfers, Transaction, CashierCheck
from user_management.models import User


# Create your views here.

@login_required
def sendFunds(request):
    from_accounts = Account.objects.filter(user_id=request.user.user_id).exclude(account_type="CREDIT")
    if request.POST:
        account_form = FundTransferForm()
        email_form = FundTransferFormEmail()
        phone_form = FundTransferFormPhone()
        account_form.fields['from_account'].queryset = from_accounts
        email_form.fields['from_account'].queryset = from_accounts
        phone_form.fields['from_account'].queryset = from_accounts

        context_name = "unknown_form"
        if request.POST['formId'] == 'ACCOUNT':
            form = FundTransferForm(request.POST)
            context_name = "account_form"
        elif request.POST['formId'] == 'EMAIL':
            form = FundTransferFormEmail(request.POST)
            context_name = "email_form"
        elif request.POST['formId'] == 'PHONE':
            form = FundTransferFormPhone(request.POST)
            context_name = "phone_form"

        context = {'formId': request.POST['formId'], 'cardHeader': 'Send Funds'}
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
        context[context_name] = form

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
            context['request_received'] = True
    else:
        context = {'formId': 'ACCOUNT', 'cardHeader': 'Send Funds'}
        account_form = FundTransferForm()
        email_form = FundTransferFormEmail()
        phone_form = FundTransferFormPhone()
        account_form.fields['from_account'].queryset = from_accounts
        email_form.fields['from_account'].queryset = from_accounts
        phone_form.fields['from_account'].queryset = from_accounts
        context['account_form'] = account_form
        context['email_form'] = email_form
        context['phone_form'] = phone_form

    context['pastFundTransfersData'] = {'headers': [u'Transaction Id', u'Requested From', u'Requested By', u'Amount', u'Status'],
                                        'rows': []}
    curUserAccounts = Account.objects.filter(user_id=request.user.user_id).only('account_id')
    for e in FundTransfers.objects.filter(is_request=False).filter(from_account__in=curUserAccounts).order_by('-request_id'):
        context['pastFundTransfersData']['rows'].append([
            e.request_id,
            str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
            " " + e.from_account.user_id.last_name,
            str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
            " " + e.to_account.user_id.last_name,
            e.amount,
            e.status
        ])
    return render(request, 'transaction_management/transfers.html', context)

@login_required
def receiveFunds(request):
    to_accounts = Account.objects.filter(user_id=request.user.user_id).exclude(account_type="CREDIT")
    context = {'formId': 'ACCOUNT', 'cardHeader': 'Request Funds'}
    if request.POST:
        if request.POST['formId'] == 'ACCOUNT':
            form = FundRequestForm(request.POST)
        elif request.POST['formId'] == 'EMAIL':
            form = FundRequestFormEmail(request.POST)
        elif request.POST['formId'] == 'PHONE':
            form = FundRequestFormPhone(request.POST)
        context['formId'] = request.POST['formId']
        account_form = FundRequestForm()
        email_form = FundRequestFormEmail()
        phone_form = FundRequestFormPhone()
        account_form.fields['to_account'].queryset = to_accounts
        email_form.fields['to_account'].queryset = to_accounts
        phone_form.fields['to_account'].queryset = to_accounts
        form.fields['to_account'].queryset = to_accounts
        context['account_form'] = account_form
        context['email_form'] = email_form
        context['phone_form'] = phone_form
        if request.POST['formId'] == 'ACCOUNT':
            context['account_form'] = form
        elif request.POST['formId'] == 'EMAIL':
            context['email_form'] = form
        elif request.POST['formId'] == 'PHONE':
            context['phone_form'] = form
        if form.is_valid():
            s = request.POST.dict()
            if s['formId'] == 'EMAIL':
                s['from_account'] = User.objects.get(email=s['from_email']).primary_account
            elif s['formId'] == 'PHONE':
                s['from_account'] = User.objects.get(phone_number=s['from_phone']).primary_account
            form = FundRequestForm(s, request.user)
            instance = form.save(commit=False)
            instance.transfer_type = s['formId']
            instance.is_request = True
            instance.save()
            context['request_received'] = True
    else:
        
        account_form = FundRequestForm()
        email_form = FundRequestFormEmail()
        phone_form = FundRequestFormPhone()
        account_form.fields['to_account'].queryset = to_accounts
        email_form.fields['to_account'].queryset = to_accounts
        phone_form.fields['to_account'].queryset = to_accounts
        context['account_form'] = account_form
        context['email_form'] = email_form
        context['phone_form'] = phone_form

    context['pastFundTransfersData'] = {'headers': [u'Transaction Id', u'Requested From', u'Requested By', u'Amount', u'Status'],
                                        'rows': []}
    curUserAccounts = Account.objects.filter(user_id=request.user.user_id).only('account_id')
    for e in FundTransfers.objects.filter(is_request=True).filter(to_account__in=curUserAccounts).order_by('-request_id'):
        context['pastFundTransfersData']['rows'].append([
            e.request_id,
            str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
            " " + e.from_account.user_id.last_name,
            str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
            " " + e.to_account.user_id.last_name,
            e.amount,
            e.status
        ])
    return render(request, 'transaction_management/transfers.html', context)

@login_required
def fundRequests(request):
    if request.POST:
        context = {"pendingFundTransfersData": {"error": ""}}
        curFundObj = FundTransfers.objects.get(
            request_id=int(request.POST['request_id']))
        if(Account.objects.get(account_id=curFundObj.from_account_id).user_id.user_id == request.user.user_id):
            if(FundTransfers.objects.get(request_id=int(request.POST['request_id'])).status) == 'NEW':
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
                    FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(status=request.POST['status'])
            else:
                context["pendingFundTransfersData"]["error"] = "Already approved/rejected"
        else:
            context["pendingFundTransfersData"]["error"] = "Approve transaction requests received to your account"
        return render(request, 'transaction_management/pendingFundTransfers.html', context)
    else:
        context = {}
        context['pendingFundTransfersData'] = {
            'headers': [u'Transaction Id', u'Requested From', u'Requested By', u'Amount', u'Status', u'Approve', u'Reject'],
            'rows': [],
            'error': ""
        }
        curUserAccounts = Account.objects.filter(user_id=request.user.user_id).only('account_id')
        for e in FundTransfers.objects.filter(is_request=True).filter(status="NEW").filter(from_account__in=curUserAccounts):
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
            'headers': [u'Transaction Id', u'Requested From', u'Requested By', u'Amount', u'Status'],
            'rows': []
        }
        for e in FundTransfers.objects.filter(is_request=True).filter(~Q(status="NEW")).filter(from_account__in=curUserAccounts):
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


def t1_check(user):
    return user.user_type == "T1"


def t2_check(user):
    return user.user_type == "T2"


@login_required
@user_passes_test(t1_check)
def nonCriticalPendingFundTransfers(request):
    if request.POST:
        context = {"pendingFundTransfersData": {"error": ""}}
        curFundObj = FundTransfers.objects.get(
            request_id=int(request.POST['request_id']))
        if curFundObj.amount < 1000:
            if(FundTransfers.objects.get(request_id=int(request.POST['request_id'])).status) == 'NEW':
                if (request.POST['status'] == "APPROVED"):
                    curBal = Account.objects.get(
                        account_id=curFundObj.from_account_id).account_balance
                    if curBal >= curFundObj.amount:
                        FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(
                            status=request.POST['status'])
                        Account.objects.filter(account_id=curFundObj.from_account_id).update(
                            account_balance=curBal - curFundObj.amount)
                        Account.objects.filter(account_id=curFundObj.to_account_id).update(
                            account_balance=Account.objects.get(
                                account_id=curFundObj.to_account_id).account_balance + curFundObj.amount)
                    else:
                        context["pendingFundTransfersData"]["error"] = "Rejected: Insufficient funds"
                        FundTransfers.objects.filter(request_id=int(
                            request.POST['request_id'])).update(status="REJECTED")
                else:
                    FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(
                        status=request.POST['status'])
            else:
                context["pendingFundTransfersData"]["error"] = "Already approved/rejected"
        return render(request, 'transaction_management/pendingFundTransfers.html', context)
    else:
        context = {}
        context['pendingFundTransfersData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status', u'Approve', u'Reject'],
            'rows': [],
            'error': ""
        }
        for e in FundTransfers.objects.filter(is_request=False).filter(status="NEW").filter(amount__lt=1000):
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
        for e in FundTransfers.objects.filter(is_request=False).filter(~Q(status="NEW")).filter(amount__lt=1000):
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


@login_required
@user_passes_test(t2_check)
def criticalPendingFundTransfers(request):
    if request.POST:
        context = {"pendingFundTransfersData": {"error": ""}}
        curFundObj = FundTransfers.objects.get(
            request_id=int(request.POST['request_id']))
        if curFundObj.amount >= 1000:
            if(FundTransfers.objects.get(request_id=int(request.POST['request_id'])).status) == 'NEW':
                if (request.POST['status'] == "APPROVED"):
                    curBal = Account.objects.get(
                        account_id=curFundObj.from_account_id).account_balance
                    if curBal >= curFundObj.amount:
                        FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(
                            status=request.POST['status'])
                        Account.objects.filter(account_id=curFundObj.from_account_id).update(
                            account_balance=curBal - curFundObj.amount)
                        Account.objects.filter(account_id=curFundObj.to_account_id).update(
                            account_balance=Account.objects.get(
                                account_id=curFundObj.to_account_id).account_balance + curFundObj.amount)
                    else:
                        context["pendingFundTransfersData"]["error"] = "Rejected: Insufficient funds"
                        FundTransfers.objects.filter(request_id=int(
                            request.POST['request_id'])).update(status="REJECTED")
                else:
                    FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(
                        status=request.POST['status'])
            else:
                context["pendingFundTransfersData"]["error"] = "Already approved/rejected"
            
        return render(request, 'transaction_management/pendingFundTransfers.html', context)
    else:
        context = {'pendingFundTransfersData': {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status', u'Approve', u'Reject'],
            'rows': [],
            'error': ""
        }}
        for e in FundTransfers.objects.filter(is_request=False).filter(status="NEW").filter(amount__gte=1000):
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
        for e in FundTransfers.objects.filter(is_request=False).filter(~Q(status="NEW")).filter(amount__gte=1000):
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

@login_required
@user_passes_test(t1_check)
def nonCriticalPendingTransactions(request):
    if request.POST:
        context = {"pendingTransactionsData": {"error": ""}}
        curFundObj = Transaction.objects.get(
            request_id=int(request.POST['request_id']))
        if curFundObj.amount < 1000:
            if(Transaction.objects.get(request_id=int(request.POST['request_id'])).status) == 'NEW':
                if (request.POST['status'] == "APPROVED"):
                    curBal = Account.objects.get(
                        account_id=curFundObj.from_account_id).account_balance
                    if curBal >= curFundObj.amount:
                        Transaction.objects.filter(request_id=int(request.POST['request_id'])).update(
                            status=request.POST['status'])
                        Account.objects.filter(account_id=curFundObj.from_account_id).update(
                            account_balance=curBal - curFundObj.amount)
                        Account.objects.filter(account_id=curFundObj.to_account_id).update(account_balance=Account.objects.get(
                            account_id=curFundObj.to_account_id).account_balance + curFundObj.amount)
                    else:
                        context["pendingTransactionsData"]["error"] = "Rejected: Insufficient funds"
                        Transaction.objects.filter(request_id=int(
                            request.POST['request_id'])).update(status="REJECTED")
                else:
                    Transaction.objects.filter(request_id=int(request.POST['request_id'])).update(
                        status=request.POST['status'])
            else:
                context["pendingTransactionsData"]["error"] = "Already approved/rejected"
        return render(request, 'transaction_management/pendingTransactions.html', context)
    else:
        context = {}
        context['pendingTransactionsData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status', u'Approve', u'Reject'],
            'rows': [],
            'error': ""
        }
        for e in Transaction.objects.filter(status="NEW").filter(amount__lt=1000):
            context['pendingTransactionsData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
                " " + e.to_account.user_id.last_name,
                e.amount,
                e.status
            ])

        context['actionedTransactionsData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status'],
            'rows': []
        }
        for e in Transaction.objects.filter(~Q(status="NEW")).filter(amount__lt=1000):
            context['actionedTransactionsData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
                " " + e.to_account.user_id.last_name,
                e.amount,
                e.status
            ])
        return render(request, 'transaction_management/pendingTransactions.html', context)

@login_required
@user_passes_test(t2_check)
def criticalPendingTransactions(request):
    if request.POST:
        context = {"pendingTransactionsData": {"error": ""}}
        curFundObj = Transaction.objects.get(
            request_id=int(request.POST['request_id']))
        if curFundObj.amount >= 1000:
            if(Transaction.objects.get(request_id=int(request.POST['request_id'])).status) == 'NEW':
                if (request.POST['status'] == "APPROVED"):
                    curBal = Account.objects.get(
                        account_id=curFundObj.from_account_id).account_balance
                    if curBal >= curFundObj.amount:
                        Transaction.objects.filter(request_id=int(request.POST['request_id'])).update(
                            status=request.POST['status'])
                        Account.objects.filter(account_id=curFundObj.from_account_id).update(
                            account_balance=curBal - curFundObj.amount)
                        Account.objects.filter(account_id=curFundObj.to_account_id).update(account_balance=Account.objects.get(
                            account_id=curFundObj.to_account_id).account_balance + curFundObj.amount)
                    else:
                        context["pendingTransactionsData"]["error"] = "Rejected: Insufficient funds"
                        Transaction.objects.filter(request_id=int(
                            request.POST['request_id'])).update(status="REJECTED")
                else:
                    Transaction.objects.filter(request_id=int(request.POST['request_id'])).update(
                        status=request.POST['status'])
            else:
                context["pendingTransactionsData"]["error"] = "Already approved/rejected"
        return render(request, 'transaction_management/pendingTransactions.html', context)
    else:
        context = {'pendingTransactionsData': {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status', u'Approve', u'Reject'],
            'rows': [],
            'error': ""
        }}
        for e in Transaction.objects.filter(status="NEW").filter(amount__gte=1000):
            context['pendingTransactionsData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
                " " + e.to_account.user_id.last_name,
                e.amount,
                e.status
            ])

        context['actionedTransactionsData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status'],
            'rows': []
        }
        for e in Transaction.objects.filter(~Q(status="NEW")).filter(amount__gte=1000):
            context['actionedTransactionsData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name +
                " " + e.to_account.user_id.last_name,
                e.amount,
                e.status
            ])
        return render(request, 'transaction_management/pendingTransactions.html', context)


@login_required
def transaction(request):
    from_accounts_debit = Account.objects.filter(user_id=request.user.user_id).exclude(account_type="CREDIT")
    from_accounts_credit = Account.objects.filter(user_id=request.user.user_id).filter(account_type="CREDIT")
    if request.POST:
        if request.POST['formId'] == 'DEBIT':
            form = TransactionForm(request.POST)
            form.fields['from_account'].queryset = from_accounts_debit
        elif request.POST['formId'] == 'CREDIT':
            form = TransactionForm(request.POST)
            form.fields['from_account'].queryset = from_accounts_credit
        context = {'formId': request.POST['formId']}
        debit_form = FundTransferForm()
        credit_form = FundTransferFormEmail()
        debit_form.fields['from_account'].queryset = from_accounts_debit
        credit_form.fields['from_account'].queryset = from_accounts_credit
        context['debit_form'] = debit_form
        context['credit_form'] = credit_form
        if request.POST['formId'] == 'ACCOUNT':
            context['debit_form'] = form
        elif request.POST['formId'] == 'CREDIT':
            context['credit_form'] = form
        if form.is_valid():
            instance = form.save(commit=False)
            instance.transfer_type = request.POST['formId']
            instance.save()
            context['request_received'] = True
        return render(request, 'transaction_management/trans_create.html', context)
    else:
        context = {'formId': 'DEBIT'}
        debit_form = TransactionForm()
        credit_form = TransactionForm()
        debit_form.fields['from_account'].queryset = from_accounts_debit
        credit_form.fields['from_account'].queryset = from_accounts_credit
        context['debit_form'] = debit_form
        context['credit_form'] = credit_form
        return render(request, 'transaction_management/trans_create.html', context)


@login_required
def transaction_view(request, id):
    obj = Transaction.objects.get(request_id=id)
    context = {
        "obj": obj
    }
    return render(request, "transaction_management/trans_view.html", context)


@login_required
def trans_list_view(request):
    object_list = Transaction.objects.all()
    context = {
        "object_list": object_list
    }
    return render(request, "transaction_management/trans_list.html", context)


@login_required
def cashierCheck(request):
    from_accounts = Account.objects.filter(user_id=request.user.user_id).exclude(account_type="CREDIT")
    if request.POST:
        if request.POST['formId'] == 'ACCOUNT':
            form = CashierCheckForm(request.POST)
        context = {'formId': request.POST['formId']}
        account_form = CashierCheckForm()
        account_form.fields['from_account'].queryset = from_accounts
        form.fields['from_account'].queryset = from_accounts
        context['account_form'] = account_form
        if request.POST['formId'] == 'ACCOUNT':
            context['account_form'] = form
        if form.is_valid():
            s = request.POST.dict()
            form = CashierCheckForm(s, request.user)
            instance = form.save(commit=False)
            instance.transfer_type = s['formId']
            instance.save()
            context['request_received'] = True
        return render(request, 'transaction_management/cashierCheck.html', context)
    else:
        context = {'formId': 'ACCOUNT'}
        account_form = CashierCheckForm()
        account_form.fields['from_account'].queryset = from_accounts
        context['account_form'] = account_form
        context['approvedCashierChecksData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status'],
            'rows': []
        }
        for e in CashierCheck.objects.filter(status="APPROVED"):
            context['approvedCashierChecksData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                e.pay_to_the_order_of,
                e.amount
            ])
        return render(request, 'transaction_management/cashierCheck.html', context)


@login_required
@user_passes_test(t1_check)
def pendingCashierChecks(request):
    if request.POST:
        context = {"pendingCashierChecksData": {"error": ""}}
        curFundObj = CashierCheck.objects.get(
            request_id=int(request.POST['request_id']))
        if(CashierCheck.objects.get(request_id=int(request.POST['request_id'])).status) == 'NEW':
            if (request.POST['status'] == "APPROVED"):
                curBal = Account.objects.get(
                    account_id=curFundObj.from_account_id).account_balance
                if curBal >= curFundObj.amount + 10:
                    CashierCheck.objects.filter(request_id=int(request.POST['request_id'])).update(
                        status=request.POST['status'])
                    Account.objects.filter(account_id=curFundObj.from_account_id).update(
                        account_balance=curBal - curFundObj.amount - 10)
                else:
                    context["pendingCashierChecksData"]["error"] = "Rejected: Insufficient funds"
                    CashierCheck.objects.filter(request_id=int(
                        request.POST['request_id'])).update(status="REJECTED")
            else:
                CashierCheck.objects.filter(request_id=int(request.POST['request_id'])).update(
                    status=request.POST['status'])
        else:
            context["pendingCashierChecksData"]["error"] = "Already approved/rejected"
        return render(request, 'transaction_management/pendingCashierChecks.html', context)
    else:
        context = {}
        context['pendingCashierChecksData'] = {
            'headers': [u'Transaction Id', u'From Account', u'Pay to the Order of', u'Amount', u'Status', u'Approve',
                        u'Reject'],
            'rows': [],
            'error': ""
        }
        for e in CashierCheck.objects.filter(status="NEW"):
            context['pendingCashierChecksData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                e.pay_to_the_order_of,
                e.amount,
                e.status
            ])

        context['actionedCashierChecksData'] = {
            'headers': [u'Transaction Id', u'From Account', u'Pay to the Order of', u'Amount', u'Status'],
            'rows': []
        }
        for e in CashierCheck.objects.filter(~Q(status="NEW")):
            context['actionedCashierChecksData']['rows'].append([
                e.request_id,
                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name +
                " " + e.from_account.user_id.last_name,
                e.pay_to_the_order_of,
                e.amount,
                e.status
            ])
        return render(request, 'transaction_management/pendingCashierChecks.html', context)
