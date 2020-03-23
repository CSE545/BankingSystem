#from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
#from django.contrib.auth.signals import user_login_failed
from django.db import models
#rom django.db.models.signals import post_save
#from django.dispatch import receiver


# Create your models here.
class EMP_Transaction(models.Model):
    Action = (
        ('create', 'Creating a Transaction'),
        ('Authorize', 'Authorizing a transaction'),
        ('view', 'viewing specific transaction'),
    )

    action = models.CharField(max_length=32, choices=Action, default='view')


class EMP_Transaction_Create(models.Model):
    name = models.CharField(max_length=32, default=None,
                            verbose_name=u"Sender", help_text=u"Choose the sending account...")
    to = models.CharField(max_length=32, default=None,
                            verbose_name=u"Recipient", help_text=u"Choose the recipient account...")
    transaction_amount = models.DecimalField(decimal_places=2, max_digits=10, default=None,
                                             verbose_name=u"Amount", help_text=u"Choose an amount to send...")

    transaction_amount_credit=models.DecimalField(decimal_places=2, max_digits=7, default=None, 
                                             verbose_name=u"Amount", help_text=u"Choose an amount to send...")
    
    def get_absolute_url(self):
        return f"/trans/list/view/{self.id}/"
