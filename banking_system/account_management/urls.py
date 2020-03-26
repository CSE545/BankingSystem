from django.urls import path
from . import views

app_name = 'account_management'

urlpatterns = [
    path('open_account/', views.open_account, name="open_account"),
    path('view_requests/', views.view_requests, name="view_requests"),
    path('view_accounts/', views.view_accounts, name="view_accounts"),
    path('deposit/', views.deposit, name="deposit"),
    path('withdraw/', views.withdraw, name="withdraw")
]
