from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from account_management.forms import BankAccountForm, CustomerAccountForm
from django.core.exceptions import PermissionDenied
import datetime
from io import BytesIO

import xhtml2pdf.pisa as pisa
from account_management.forms import BankAccountForm, StatementRequestForm
from account_management.models import AccountRequests, Account, DepositRequest
from account_management.utility.manage_accounts import create_account_for_current_request
from account_management.utility.manage_accounts import create_deposit_request
from account_management.utility.manage_accounts import update_deposit_request, withdraw_money
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from transaction_management.models import FundTransfers, Transaction
from user_management.models import User
from user_management.utility.twofa import generate_otp, save_otp_in_db  # , send_otp


class PDFRender:
    """
    Referenced from Ben Cleary's work on his public GitHub and provided in a GitHub Gist.
     * @author Ben Cleary
     * @url https://gist.github.com/bencleary/1cb0f951362d3fdac954e0ab94d2e6bd/revisions
     * @referenced 3/28/20
    """

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


def open_customer_account(request):
    """ Used by Tier 2 employees to open new customer bank account."""
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


@login_required
def delete_customer_bank_accounts(request):
    """ Tier 2 employees deleting customer accounts. """
    context = {}
    if request.POST:
        account_number = int(request.POST['account_number'])
        # Checking if the selected account is the primary account of the customer
        results = User.objects.filter(primary_account_id=account_number)
        if results.count() > 0:
            # This account is the customer's primary account
            for result in results:
                user_id = result.user_id
            # Finding if user have another account that can be made the primary account
            customer_accounts = Account.objects.filter(user_id=user_id)
            for acc in customer_accounts:
                if acc.account_id != account_number:
                    if acc.account_type == 'CREDIT':
                        continue
                    # Update the primary account for the user
                    user = User.objects.get(user_id=user_id)
                    user.primary_account_id = acc.account_id
                    user.save()
                    break

        Account.objects.filter(account_id=account_number).delete()

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
    if request.POST:
        context['account_deleted'] = True
    return render(request, 'account_management/delete_customer_bank_accounts.html', context)


@login_required
def view_customer_accounts(request, pk=None):
    """ Tier 2 employees accessing customer accounts. """
    account_types = (
        "CHECKING",
        "SAVINGS",
        "CREDIT")
    context = {}
    if pk and request.POST:
        account_number = int(request.POST['account_number'])
        account_type = request.POST['account_type']
        account = Account.objects.get(account_id=account_number)
        account.account_type = account_type
        account.save()
    elif pk:
        print("In here!!")
        context['account_selected'] = True
        current_account = Account.objects.get(account_id=pk)
        context['choices'] = account_types
        context['selected_choice'] = current_account.account_type
        context['user_accounts'] = {
            'headers': ['Account number', 'Account type', 'Account balance'],
            'details': {
                'account_balance': current_account.account_balance,
                'account_number': current_account.account_id,
                'account_type': current_account.account_type,
            }
        }
        return render(request, 'account_management/view_customer_bank_accounts.html', context)
    else:
        customer_bank_accounts = Account.objects.filter()
        context['account_details'] = {
            'headers': ['Account number', 'Account type', 'Account balance', 'Action'],
            'accounts': []
        }
        context['select_account'] = True
        for acc in customer_bank_accounts:
            context['account_details']['accounts'].append([
                acc.account_id,
                acc.account_type,
                acc.account_balance
            ])
    return render(request, 'account_management/view_customer_bank_accounts.html', context)


@login_required
def view_customer_accounts_t1(request):
    """ Used by tier 1 emplloyees to view customer bank accounts. """
    customer_bank_accounts = Account.objects.filter()
    context = {}
    context['account_details'] = {
        'headers': ['Account number', 'Account type', 'Account balance'],
        'accounts': []
    }
    for acc in customer_bank_accounts:
        context['account_details']['accounts'].append([
            acc.account_id,
            acc.account_type,
            acc.account_balance
        ])
    return render(request, 'account_management/view_customer_bank_accounts_t1.html', context)


class BankStatementRow:
    def __init__(self, description="No Description", transaction_type="Unknown", amount="$0.00", status="Pending"):
        self.info = {"description": description, "transaction_type": transaction_type,
                     "amount": amount, "status": status, "outbound": None, "date": None}

    def outbound(self, outbound):
        self.info["outbound"] = outbound

    def description(self, description):
        self.info["description"] = description

    def transaction_type(self, transaction_type):
        self.info["transaction_type"] = transaction_type

    def amount(self, amount):
        self.info["amount"] = "$%.2f" % amount

    def status(self, status):
        self.info["status"] = status

    def date(self, date):
        self.info["date"] = date


@login_required
def generate_statement(request):
    user_accounts = Account.objects.filter(user_id=request.user)
    if request.POST:
        account_id = request.POST["account"].split(",")[0].split(":")[
            1].strip()
        account_name = request.POST["account"].split(",")[3].split(":")[
            1].strip()
        start_date_string = request.POST["start_date"]
        end_date_string = request.POST["end_date"]
        received_otp = request.POST["otp"]
        try:
            transfer_from = list(FundTransfers.objects.filter(
                from_account_id=account_id, created_date__range=[start_date_string, end_date_string]))
            transfer_to = list(FundTransfers.objects.filter(
                to_account_id=account_id, created_date__range=[start_date_string, end_date_string]))

            transaction_from = list(Transaction.objects.filter(from_account_id=account_id,
                                                               created_date__range=[start_date_string,
                                                                                    end_date_string]))
            transaction_to = list(Transaction.objects.filter(to_account_id=account_id,
                                                             created_date__range=[start_date_string, end_date_string]))

            transfer_to += transaction_to
            transfer_from += transaction_from

            result = []
            for transfer in transfer_to:
                temp = BankStatementRow()
                temp.description("Sent from %s (%s)" % (transfer.from_account.user_id.get_full_name(),
                                                        transfer.from_account.user_id.email))
                temp.transaction_type(transfer.transfer_type)
                temp.amount(transfer.amount)
                temp.status(transfer.status)
                temp.outbound(False)
                temp.date(transfer.created_date)
                result.append(temp.info)

            for transfer in transfer_from:
                temp = BankStatementRow()
                temp.description("Sent to %s (%s)" % (transfer.to_account.user_id.get_full_name(),
                                                      transfer.to_account.user_id.email))
                temp.transaction_type(transfer.transfer_type)
                temp.amount(transfer.amount)
                temp.status(transfer.status)
                temp.outbound(True)
                temp.date(transfer.created_date)
                result.append(temp.info)

            form = StatementRequestForm()
            form.account_list = user_accounts
            context = {"name": account_name, "accountNo": int(
                account_id), "today": datetime.datetime.today(), "result": result}
            if received_otp != str(request.user.statementotp.last_otp):
                context = {'form': form, 'user_accounts': user_accounts}
                context['invalid_otp'] = True
                return render(request, 'account_management/generate_statement.html', context)
            otp = generate_otp()
            print('otp', otp)
            user = User.objects.get(email=request.user.email)
            user.statementotp.last_otp = otp
            user.statementotp.save()
            context['otp_sent'] = True
            context['invalid_otp'] = False
            return PDFRender.render('account_management/pdfTemplate.html', context)
        except Exception as e:
            print("Data entered is not valid", e)
            form = StatementRequestForm()
            context = {'form': form, 'user_accounts': user_accounts}
            return render(request, 'account_management/generate_statement.html', context)
    else:
        form = StatementRequestForm()
        context = {'form': form, 'user_accounts': user_accounts}
        otp = generate_otp()
        print('otp', otp)
        user = User.objects.get(email=request.user.email)
        user.statementotp.last_otp = otp
        user.statementotp.save()
        context['otp_sent'] = True
        # user = get_user_phone_number(request.user.email)
        # send_otp(otp, request.user.phone_number)
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


@login_required
def deposit(request, pk=None):
    context = {}
    if pk and request.POST:
        amount = request.POST['amount']
        account_id = request.POST['account_id']
        create_deposit_request(request.user, amount, account_id)
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
