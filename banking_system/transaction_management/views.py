from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from transaction_management.forms import FundTransferForm
from user_management.models import User
from transaction_management.models import FundTransfers
from account_management.models import Account

# Create your views here.

# def load_to_accounts(request):
#     from_account_id = request.GET.get('from_account_id')
#     to_account = Account.objects.exclude(account_id=int(from_account_id))
#     return render(request, 'transaction_management/to_account_dropdown_list_options.html', {'to_account': to_account})

@login_required
def transfers(request):
    if request.POST:
        form = FundTransferForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            context = {}
            context['request_received'] = True
            print('request_received')
            return redirect('home')
        else:
            context = {}
            context['transfer_form'] = form
            return render(request, 'transaction_management/transfers.html', context)
            
    else:
        context = {}
        form = FundTransferForm(instance=request.user)
        form.fields['from_account'].queryset = Account.objects.filter(user_id=request.user.user_id)
        # form.fields['to_account'].queryset = Account.objects.only('account_balance')
        context['transfer_form'] = form
        return render(request, 'transaction_management/transfers.html', context)

def employee_check(user):
    return user.user_type in ["T1", "T2", "T3"]

@login_required
@user_passes_test(employee_check)
def pendingFundTransfers(request):
    if request.POST:
        context = {"pendingFundTransfersData": {"error": ""}}
        curFundObj = FundTransfers.objects.get(request_id=int(request.POST['request_id']))
        if(request.POST['status'] == "APPROVED"):
            curBal = Account.objects.get(account_id=curFundObj.from_account_id).account_balance
            if curBal >= curFundObj.amount:
                FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(status=request.POST['status'])
                Account.objects.filter(account_id=curFundObj.from_account_id).update(account_balance=curBal - curFundObj.amount)
                Account.objects.filter(account_id=curFundObj.to_account_id).update(account_balance=Account.objects.get(account_id=curFundObj.to_account_id).account_balance + curFundObj.amount)
            else:
                context["pendingFundTransfersData"]["error"] = "Rejected: Insufficient funds"
                FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(status="REJECTED")

        else:
            FundTransfers.objects.filter(request_id=int(request.POST['request_id'])).update(status=request.POST['status'])
        return render(request, 'transaction_management/pendingFundTransfers.html', context)
    else:
        context = {}
        context['pendingFundTransfersData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status', u'Approve', u'Reject'],
            'rows': [],
            'error': ""
        }
        for e in FundTransfers.objects.filter(status="NEW"):
            context['pendingFundTransfersData']['rows'].append([e.request_id,
                                                                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name + " " + e.from_account.user_id.last_name,
                                                                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name + " " + e.to_account.user_id.last_name,
                                                                e.amount,
                                                                e.status])

        context['actionedFundTransfersData'] = {
            'headers': [u'Transaction Id', u'From Account', u'To Account', u'Amount', u'Status'],
            'rows': []
        }
        for e in FundTransfers.objects.filter(~Q(status="NEW")):
            context['actionedFundTransfersData']['rows'].append([e.request_id,
                                                                str(e.from_account.account_id) + ":" + e.from_account.user_id.first_name + " " + e.from_account.user_id.last_name,
                                                                str(e.to_account.account_id) + ":" + e.to_account.user_id.first_name + " " + e.to_account.user_id.last_name,
                                                                e.amount,
                                                                e.status])
        return render(request, 'transaction_management/pendingFundTransfers.html', context)
