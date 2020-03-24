from django.db import models
from user_management.models import User

# Create your models here.

ACCOUNT_TYPE = (
    ("SAVINGS", "SAVINGS"),
    ("CREDIT", "CREDIT"),
    ("CHECKING", "CHECKING")
)

class StatetementManager:
     def create_statement(self, start_date, end_date, user):
        if not user:
            raise ValueError('User not known')
        if not start_date:
            raise ValueError('User must enter start date')
        if not end_date:
            raise ValueError('Users must have an end date')
        
        statementRequest = self.model(
            start_date = start_date,
            end_date = end_date,
            user = user
        )

        statementRequest.save(using=self._db)
        return statementRequest


class StatementRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name = "user_info", on_delete=models.CASCADE)
    start_date = models.DateField(blank= False)
    end_date = models.DateField(blank= False)
    def __str__(self):
        return "Statement Request ID: {0}   User: {1}  Start Date: {2} End Date: {3}".format(self.user.first_name, self.user.request_id, self.start_date, self.end_date)
    objects = StatetementManager()


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
