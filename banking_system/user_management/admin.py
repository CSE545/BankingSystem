from django.contrib import admin
from .models import User, UserLogin, UserPendingApproval, employee_info_update, CustomerInfoUpdate, OverrideRequest, UserLog
# Register your models here.

admin.site.register(User)
admin.site.register(UserLogin)
admin.site.register(StatementOtp)
admin.site.register(UserPendingApproval)
admin.site.register(UserLog)
admin.site.register(CustomerInfoUpdate)
admin.site.register(OverrideRequest)
admin.site.register(employee_info_update)
