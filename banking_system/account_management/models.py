from django.db import models
from user_management.models import User

# Create your models here.

ACCOUNT_TYPE = (
    ("SAVINGS", "SAVINGS"),
    ("CREDIT", "CREDIT"),
    ("CHECKING", "CHECKING")
)


REQUEST_STATUS = (
    ("NEW", "NEW"),
    ("APPROVED", "APPROVED"),
    ("REJECTED", "REJECTED"),
)


class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    account_type = models.CharField(
        max_length=15,
        choices=ACCOUNT_TYPE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    account_balance = models.FloatField(default=0.0)
    user_id = models.ForeignKey(
        User, default=None, on_delete=models.CASCADE, related_name='useridAccount')

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Account Id: {0},  Account Type: {1},  \
                Account Balance: {2},  User: {3}" \
                .format(self.account_id, self.account_type,
                        self.account_balance, self.user_id.first_name + " " + self.user_id.last_name)


class AccountRequests(models.Model):
    account_id = models.AutoField(primary_key=True)
    account_type = models.CharField(
        max_length=15,
        choices=ACCOUNT_TYPE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    account_balance = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS,
        default='NEW'
    )
    user_id = models.ForeignKey(
        User, default=None, on_delete=models.CASCADE, related_name='useridAccountRequests')

    def __init__(self, *args, **kwargs):
        super(AccountRequests, self).__init__(*args, **kwargs)
        self.old_status = self.status

    def __str__(self):
        return "Account Id: {0},  Account Type: {1},  \
                Account Balance: {2},  User: {3}" \
                .format(self.account_id, self.account_type,
                        self.account_balance, self.user_id.first_name + " " + self.user_id.last_name)


class DepositRequest(models.Model):
    deposit_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        User, default=None, on_delete=models.CASCADE, related_name='useridDepositRequests')
    deposit_amount = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS,
        default='NEW'
    )
    account = models.ForeignKey(
        Account, default=None, on_delete=models.CASCADE, related_name='accountidDepositRequest')

    def __init__(self, *args, **kwargs):
        super(DepositRequest, self).__init__(*args, **kwargs)
        self.old_status = self.status

    def __str__(self):
        return "Deposit Id: {0},  \
                Deposit amount: {1},  User: {2}" \
                .format(self.deposit_id,
                        self.deposit_amount, self.user_id.first_name + " " + self.user_id.last_name)
