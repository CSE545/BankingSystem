from django.urls import path, include
from . import views

app_name = 'transaction_management'

urlpatterns = [
    path('transfers/', views.transfers, name="transfers"),
    path('pendingFundTransfers/', views.pendingFundTransfers, name="pendingFundTransfers")
    path('trans/', transaction_main, name="trans_main"),
    path('trans/create/', trans_create, name="create"),
    path('trans/list/view/<int:id>/', transaction_view, name="trans_view"),
    path('trans/list/', trans_list_view, name="list"),
    path('trans/details/', transaction_details, name="list"),
    path('trans/create_credit/', trans_create_credit, name="create_credit"),
    path('trans/no_create_credit/', no_transaction_details, name="create_credit")

]
