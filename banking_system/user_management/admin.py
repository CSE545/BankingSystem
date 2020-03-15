from django.contrib import admin
from .models import User, UserLogin, UserPendingApproval, UserLog
# Register your models here.

admin.site.register(User)
admin.site.register(UserLogin)
admin.site.register(UserPendingApproval)
admin.site.register(UserLog)