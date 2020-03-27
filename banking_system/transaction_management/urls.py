from django.urls import path, include
from . import views

app_name = 'transaction_management'

urlpatterns = [
    path('transfers/', views.transfers, name="transfers"),
    path('pendingFundTransfers/', views.pendingFundTransfers, name="pendingFundTransfers"),
    path('trans/create/', views.transaction, name="create"),
    path('trans/list/<int:id>/', views.transaction_view, name="trans_view"),
    path('trans/list/', views.trans_list_view, name="list"),
]
