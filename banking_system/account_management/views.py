from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account_management.forms import BankAccountForm, StatementRequestForm
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from account_management.models import AccountRequests, Account
from user_management.models import User
from transaction_management.models import FundTransfers
from django import forms
from account_management.utility.manage_accounts import create_account_for_current_request
from reportlab.pdfgen import canvas
import datetime
from django.http import FileResponse
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.db.models import Q


"""
 * Referenced from Ben Cleary's work on his public GitHub and provided in a GitHub Gist.
 * @author Ben Cleary
 * @url https://gist.github.com/bencleary/1cb0f951362d3fdac954e0ab94d2e6bd/revisions
 * @referenced 3/28/20
"""

class Render:
    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

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
    if request.POST:
        User.objects.filter(user_id=request.user.user_id).update(primary_account=request.POST['account_num'])
    context = {}
    context['account_details'] = {
        'headers': ['Account number', 'Account type', 'Account balance', 'Action'],
        'accounts': []
    }
    user_accounts = Account.objects.filter(user_id=request.user)
    primary_account = User.objects.get(user_id=request.user.user_id).primary_account
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


@login_required
def generate_statement(request):
    user_accounts = Account.objects.filter(user_id=request.user)
    if request.POST:
        account_id = request.POST["account"].split(",")[0].split(":")[1].strip()
        account_name = request.POST["account"].split(",")[3].split(":")[1].strip()
        start_date_string = request.POST["start_date"]
        end_date_string = request.POST["end_date"]
        start_date = datetime.datetime.strptime(start_date_string, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_string, '%Y-%m-%d')
        transactions_from =FundTransfers.objects.filter(from_account_id = account_id)
        transactions_from = transactions_from.filter(date__range=[start_date_string,end_date_string])
        transactions_to = FundTransfers.objects.filter(to_account_id = account_id)
        transactions_to = transactions_to.filter(date__range=[start_date_string,end_date_string])
        result =[]
        for i in transactions_to:
            temp =i.__dict__
            temp["description"] = i.from_account.user_id.get_full_name()
            result.append(temp)
            
        for i in transactions_from:
            temp =i.__dict__
            temp["description"] = i.from_account.user_id.get_full_name()
            result.append(temp)
            
        context = {}
        form = StatementRequestForm()
        form.account_list = user_accounts
        context['form'] = form
        params= {"name":account_name,"accountNo": int(account_id),"today":datetime.datetime.today(), "result": result}
        return Render.render('account_management/pdfTemplate.html', params)
        
    else:
        context = {}
        form = StatementRequestForm()
        context['form'] = form
        context['user_accounts'] = user_accounts
        return render(request, 'account_management/generate_statement.html', context)


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
