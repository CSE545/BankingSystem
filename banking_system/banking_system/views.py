from django.contrib.auth.decorators import login_required
from user_management.models import User, CustomerInfoUpdate, OverrideRequest
from django.shortcuts import render
from account_management.models import Account, DepositRequest, AccountRequests
from django.db.models import Sum
from transaction_management.models import FundTransfers, CashierCheck

@login_required
def homepage(request):
    context = {}
    email = request.user.email
    user = User.objects.get(email=email)
    context['user_type'] = user.user_type
    print(user.user_type)
    if user.user_type == "CUSTOMER":
        tile = getCustomerTile(user)
    elif user.user_type == 'T1':
        tile = getT1Tile(user)
    elif user.user_type == 'T2':
        tile = getT2Tile(user)
    elif user.user_type == 'T3':
        tile = getT2Tile(user)
    context['tilesData'] = tile
    return render(request, 'homepage.html', context)
   

def getCustomerTile(user):
    customerTile = []
    tile = {}
    lines = []
    lines.append("Number of accounts: " + str(Account.objects.filter(user_id=user.user_id).count()))
    lines.append("Available balance: " + str(Account.objects.filter(user_id=user.user_id).exclude(account_type="CREDIT").aggregate(Sum('account_balance'))['account_balance__sum']))
    lines.append("Statements balance: " + str(Account.objects.filter(user_id=user.user_id).filter(account_type="CREDIT").aggregate(Sum('account_balance'))['account_balance__sum']))
    tile['lines'] = lines
    tile['class'] = 'tile-color1'
    customerTile.append(tile)
    tile = {}
    lines = []
    curUserAccounts = Account.objects.filter(user_id=user.user_id).only('account_id')
    lines.append("Number of fund requests received: " + str(FundTransfers.objects.filter(is_request=True).filter(status="NEW").filter(from_account__in=curUserAccounts).count()))
    lines.append("Amount requested: " + str(FundTransfers.objects.filter(is_request=True).filter(status="NEW").filter(from_account__in=curUserAccounts).aggregate(Sum('amount'))['amount__sum']))
    tile['lines'] = lines
    tile['class'] = 'tile-color2'
    customerTile.append(tile)
    tile = {}
    lines = []
    lines.append("Number of pending fund requests: " + str(FundTransfers.objects.filter(is_request=True).filter(status="NEW").filter(from_account__in=curUserAccounts).count()))
    lines.append("Number of pending fund transfer requests: " + str(FundTransfers.objects.filter(is_request=False).filter(status="NEW").filter(from_account__in=curUserAccounts).count()))
    tile['lines'] = lines
    tile['class'] = 'tile-color3'
    customerTile.append(tile)
    return customerTile

def getT1Tile(user):
    t1Tile = []
    tile = {}
    lines = []
    lines.append("Number of deposit requests: " + str(DepositRequest.objects.filter(status='NEW').count()))
    lines.append("Number of fund transfer requests: " + str(FundTransfers.objects.filter(is_request=False).filter(status="NEW").filter(amount__lt=1000).count()))
    lines.append("Number of cashier check requests: " + str(CashierCheck.objects.filter(status="NEW").count()))
    tile['lines'] = lines
    tile['class'] = 'tile-color1'
    t1Tile.append(tile)
    tile = {}
    lines = []
    lines.append("Number of override requests: " + str(OverrideRequest.objects.filter(status='NEW').count()))
    lines.append("Number of information update requests: " + str(CustomerInfoUpdate.objects.filter(status="NEW").count()))
    tile['lines'] = lines
    tile['class'] = 'tile-color2'
    t1Tile.append(tile)
    return t1Tile

def getT2Tile(user):
    t2Tile = []
    tile = {}
    lines = []
    lines.append("Number of account requests: " + str(AccountRequests.objects.filter(status='NEW').count()))
    lines.append("Number of help & requests: " + str(OverrideRequest.objects.filter(status='NEW').count()))
    tile['lines'] = lines
    tile['class'] = 'tile-color1'
    t2Tile.append(tile)
    tile = {}
    lines = []
    lines.append("Number of fund transfer requests: " + str(FundTransfers.objects.filter(is_request=False).filter(status="NEW").filter(amount__gte=1000).count()))
    tile['lines'] = lines
    tile['class'] = 'tile-color2'
    t2Tile.append(tile)
    return t2Tile

def getT3Tile(user):
    t3Tile = []
    tile = {}
    lines = []
    lines.append("Number of deposit requests: " + str(DepositRequest.objects.filter(status='NEW').count()))
    lines.append("Number of fund transfer requests: " + str(FundTransfers.objects.filter(is_request=False).filter(status="NEW").filter(amount__lt=1000).count()))
    lines.append("Number of cashier check requests: " + str(CashierCheck.objects.filter(status="NEW").count()))
    tile['lines'] = lines
    tile['class'] = 'tile-color1'
    t3Tile.append(tile)
    tile = {}
    lines = []
    lines.append("Number of override requests: " + str(OverrideRequest.objects.filter(status='NEW').count()))
    lines.append("Number of information update requests: " + str(CustomerInfoUpdate.objects.filter(status="NEW").count()))
    tile['lines'] = lines
    tile['class'] = 'tile-color2'
    t3Tile.append(tile)
    return t3Tile

