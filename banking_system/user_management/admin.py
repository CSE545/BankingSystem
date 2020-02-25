from django.contrib import admin
from .models import User, UserLogin
# Register your models here.

admin.site.register(User)
admin.site.register(UserLogin)
