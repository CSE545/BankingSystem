from django.contrib import admin
from .models import Account, AccountRequests

# Register your models here.
admin.site.register(Account)
admin.site.register(AccountRequests)
