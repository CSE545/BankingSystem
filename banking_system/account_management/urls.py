from django.urls import path, re_path
from . import views
from django.views.generic import TemplateView
from django.conf.urls import url

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
    path('customer_deposits/', views.customer_deposits, name="customer_deposits"),
    path('view_customer_bank_accounts/', views.view_customer_accounts,
         name="view_customer_bank_accounts"),
    re_path(r'^view_customer_bank_accounts/(?P<pk>\d+)/$', views.view_customer_accounts,
            name="view_customer_bank_accounts_with_pk"),
    url(r'^$', TemplateView.as_view(template_name="customer_account_deletion_failed.html"),
        name='customer_account_deletion_failed'),
    path('delete_customer_bank_accounts/', views.delete_customer_bank_accounts,
         name='delete_customer_bank_accounts'),
    path('open_customer_account/', views.open_customer_account, name='open_customer_account'),
    path('view_customer_bank_accounts_t1/', views.view_customer_accounts_t1,
         name='view_customer_bank_accounts_t1')
]
