from django.contrib import admin
from .models import Account, AccountRequests, DepositRequest

# Register your models here.
admin.site.register(Account)
admin.site.register(AccountRequests)
admin.site.register(DepositRequest)
