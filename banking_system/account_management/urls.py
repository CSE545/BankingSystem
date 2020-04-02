from django.urls import path, re_path
from . import views

app_name = 'account_management'

urlpatterns = [
    path('open_account/', views.open_account, name="open_account"),
    path('view_requests/', views.view_requests, name="view_requests"),
    path('view_accounts/', views.view_accounts, name="view_accounts"),
    path('generate_statement/', views.generate_statement, name="generate_statement"),
    path('deposit/', views.deposit, name="deposit"),
    re_path(r'^deposit/(?P<pk>\d+)/$', views.deposit, name="deposit_with_pk"),
    path('withdraw/', views.withdraw, name="withdraw"),
    re_path(r'^withdraw/(?P<pk>\d+)/$', views.withdraw, name="withdraw_with_pk"),
    path('customer_deposits/', views.customer_deposits, name="customer_deposits")
]
