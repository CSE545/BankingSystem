from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'transaction_management'

urlpatterns = [
    path('transfers/', views.transfers, name="transfers"),
    path('pendingFundTransfers/', views.pendingFundTransfers, name="pendingFundTransfers"),
    path('transfers/ajax/load_to_accounts', views.load_to_accounts, name='ajax_load_to_accounts')
]
