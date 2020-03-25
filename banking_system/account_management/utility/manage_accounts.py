from account_management.models import Account


def create_account_for_current_request(user, account_type):
    Account.objects.create(
        account_type=account_type,
        user_id=user
    )
