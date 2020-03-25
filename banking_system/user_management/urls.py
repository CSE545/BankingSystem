from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

app_name = 'user_management'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', views.view_profile, name="view_profile"),
    path('transfers/', views.transfers, name="transfers"),
    path('pendingFundTransfers/', views.pendingFundTransfers, name="pendingFundTransfers"),
    path('profile/edit/', views.edit_profile, name="edit_profile"),
    path('pendingEmployeeRequests/', views.show_pending_employee_requests, name="pendingEmployeeRequests"),
    path('pendingCustomerRequests/', views.show_pending_customer_requests, name="pendingCustomerRequests"),
    url(r'^$', TemplateView.as_view(template_name="employee_edit_request_submitted.html"), name='employee_edit_request_submitted'),
    url(r'^$', TemplateView.as_view(template_name="employee_request_already_exists.html"), name='employee_request_already_exists'),
    url(r'^$', TemplateView.as_view(template_name="customer_edit_request_submitted.html"), name='customer_edit_request_submitted'),
    url(r'^$', TemplateView.as_view(template_name="customer_request_already_exists.html"), name='customer_request_already_exists')
]
