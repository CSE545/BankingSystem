from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'transaction_management'

urlpatterns = [
    path('transfers/', views.transfers, name="transfers"),
    path('pendingFundTransfers/', views.pendingFundTransfers, name="pendingFundTransfers")
]
