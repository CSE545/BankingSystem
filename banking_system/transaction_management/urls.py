from django.urls import path

from . import views

app_name = 'transaction_management'

urlpatterns = [
    path('transfers/', views.transfers, name="transfers"),
    path('nonCriticalPendingFundTransfers/', views.nonCriticalPendingFundTransfers,
         name="nonCriticalPendingFundTransfers"),
    path('criticalPendingFundTransfers/', views.criticalPendingFundTransfers, name="criticalPendingFundTransfers"),
    path('trans/create/', views.transaction, name="create"),
    path('trans/list/<int:id>/', views.transaction_view, name="trans_view"),
    path('trans/list/', views.trans_list_view, name="list"),
    path('cashierCheck/', views.cashierCheck, name="cashierCheck"),
    path('pendingCashierChecks/', views.pendingCashierChecks, name="pendingCashierChecks")
]
