from account_management.models import Account, DepositRequest


def create_account_for_current_request(user, account_type):
    account = Account.objects.create(
        account_type=account_type,
        user_id=user
    )
    return account


def create_deposit_request(user, deposit_amount):
    deposit_request = DepositRequest.objects.create(
        user_id=user,
        deposit_amount=deposit_amount
    )
    return deposit_request
