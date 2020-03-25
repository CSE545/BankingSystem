from django.urls import path, include
from . import views

app_name = 'transaction_management'

urlpatterns = [
    path('transfers/', views.transfers, name="transfers"),
    path('pendingFundTransfers/', views.pendingFundTransfers, name="pendingFundTransfers"), 
    path('trans/', views.transaction_main, name="trans_main"),
    path('trans/create/', views.trans_create, name="create"),
    path('trans/list/view/<int:id>/', views.transaction_view, name="trans_view"),
    path('trans/list/', views.trans_list_view, name="list"),
    path('trans/details/', views.transaction_details, name="list"),
    path('trans/create_credit/', views.trans_create_credit, name="create_credit"),
    path('trans/no_create_credit/', views.no_transaction_details, name="create_credit")
]
