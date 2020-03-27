from account_management.models import Account, DepositRequest


def create_account_for_current_request(user, account_type):
    account = Account.objects.create(
        account_type=account_type,
        user_id=user
    )
    return account


def create_deposit_request(user, deposit_amount, account_id):
    account = Account.objects.get(account_id=account_id)
    deposit_request = DepositRequest.objects.create(
        user_id=user,
        deposit_amount=deposit_amount,
        account=account
    )
    return deposit_request


def update_deposit_request(id, action):
    deposit_request = DepositRequest.objects.get(deposit_id=id)
    if action == 'DEPOSIT':
        deposit_request.account.account_balance += deposit_request.deposit_amount
        deposit_request.status = 'APPROVED'
        deposit_request.account.save()
        deposit_request.save()
    else:
        deposit_request.status = 'REJECTED'
        deposit_request.save()


def withdraw_money(account_id, amount):
    amount = float(amount)
    account = Account.objects.get(account_id=account_id)
    if amount > account.account_balance:
        return False
    account.account_balance -= amount
    account.save()
    return True
