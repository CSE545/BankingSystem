from django.contrib import admin

# Register your models here.
from .models import EMP_Transaction,EMP_Transaction_Create

admin.site.register(EMP_Transaction)
admin.site.register(EMP_Transaction_Create)

