from django.db import models
from user_management.models import User

# Create your models here.

ACCOUNT_TYPE = (
    ("SAVINGS", "SAVINGS"),
    ("CREDIT", "CREDIT"),
    ("CHECKING", "CHECKING")
)

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    account_type = models.CharField(
        max_length=15,
        choices=ACCOUNT_TYPE
    )
    account_balance = models.FloatField(default=0.0)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_by')
    user_id = models.ForeignKey(User, default=None, on_delete=models.CASCADE, related_name='userid')

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Account Id: {0},  Account Type: {1},  \
                Account Balance: {2},  User: {3}" \
                .format(self.account_id, self.account_type,
                        self.account_balance, self.user_id.first_name + " " + self.user_id.last_name)


