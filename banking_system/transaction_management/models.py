from django.db import models
from account_management.models import Account

# Create your models here.
REQUEST_STATUS = (
    ("NEW", "NEW"),
    ("APPROVED", "APPROVED"),
    ("REJECTED", "REJECTED"),
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
