from account_management.models import Account
from django.db import models

# Create your models here.
REQUEST_STATUS = (
    ("NEW", "NEW"),
    ("APPROVED", "APPROVED"),
    ("REJECTED", "REJECTED"),
)

TRANSFER_TYPE = (
    ("ACCOUNT", "ACCOUNT"),
    ("EMAIL", "EMAIL"),
    ("PHONE", "PHONE")
)

TRANSACTION_TYPE = (
    ("DEBIT", "DEBIT"),
    ("CREDIT", "CREDIT")
)


class FundTransfers(models.Model):
    request_id = models.AutoField(primary_key=True)
    from_account = models.ForeignKey(Account, default=None, on_delete=models.CASCADE, related_name='from_account')
    to_account = models.ForeignKey(Account, default=None, on_delete=models.CASCADE, related_name='to_account')
    amount = models.FloatField(blank=False, null=False)
    status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS,
        default='NEW'
    )
    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSFER_TYPE,
        default="ACCOUNT"
    )

    def __str__(self):
        return "Created by: {0}, Status: {1}".format(self.from_account, self.status)

    def __init__(self, *args, **kwargs):
        super(FundTransfers, self).__init__(*args, **kwargs)
        self.old_status = self.status

    def save(self, force_insert=False, force_update=False):
        if self.status != 'NEW':
            print('Status changed from NEW to {0}'.format(self.status))
            FundTransfers.objects.filter(request_id=self.request_id).update(
                status=self.status
            )
            self.delete()
        else:
            super(FundTransfers, self).save(force_insert, force_update)


class Transaction(models.Model):
    request_id = models.AutoField(primary_key=True)
    from_account = models.ForeignKey(Account, default=None, on_delete=models.CASCADE,
                                     related_name='transaction_from_account')
    to_account = models.ForeignKey(Account, default=None, on_delete=models.CASCADE,
                                   related_name='transaction_to_account')
    amount = models.FloatField(blank=False, null=False)
    status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS,
        default='NEW'
    )
    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE
    )

    def __str__(self):
        return "Created by: {0}, Status: {1}".format(self.from_account, self.status)

    def __init__(self, *args, **kwargs):
        super(Transaction, self).__init__(*args, **kwargs)

class CashierCheck(models.Model):
    request_id = models.AutoField(primary_key=True)
    from_account = models.ForeignKey(Account, default=None, on_delete=models.CASCADE, related_name='from_acc')
    pay_to_the_order_of = models.CharField(default=" ", max_length=50, blank=False, null=False)
    amount = models.FloatField(blank=False, null=False)
    status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS,
        default='NEW'
    )
    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSFER_TYPE,
        default="ACCOUNT"
    )

    def __str__(self):
        return "Created by: {0}, Status: {1}".format(self.from_account, self.status)

    def __init__(self, *args, **kwargs):
        super(CashierCheck, self).__init__(*args, **kwargs)
        self.old_status = self.status

    def save(self, force_insert=False, force_update=False):
        if self.status != 'NEW':
            print('Status changed from NEW to {0}'.format(self.status))
            CashierCheck.objects.filter(request_id=self.request_id).update(
                status=self.status
            )
            self.delete()
        else:
            super(CashierCheck, self).save(force_insert, force_update)

class HyperledgerState(models.Model):
    id = models.AutoField(primary_key=True)
    last_transaction_id = models.CharField(max_length=20, default="0")
    last_hyperledger_id = models.CharField(max_length=20, default="0")