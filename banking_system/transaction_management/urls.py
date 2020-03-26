from django.urls import path
from . import views

app_name = 'transaction_management'

urlpatterns = [
    path('transfers/', views.transfers, name="transfers"),
    path('nonCriticalPendingFundTransfers/', views.nonCriticalPendingFundTransfers, name="nonCriticalPendingFundTransfers"),
    path('criticalPendingFundTransfers/', views.criticalPendingFundTransfers, name="criticalPendingFundTransfers")
]
