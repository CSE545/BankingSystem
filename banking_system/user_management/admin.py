from django.contrib import admin
from .models import User, UserLogin, UserPendingApproval, employee_info_update
# Register your models here.

admin.site.register(User)
admin.site.register(UserLogin)
admin.site.register(UserPendingApproval)
admin.site.register(employee_info_update)
