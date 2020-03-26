from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'user_management'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', views.view_profile, name="view_profile"),
    path('profile/edit/', views.edit_profile, name="edit_profile"),
    path('pendingEmployeeRequests/', views.show_pending_employee_requests, name="pendingEmployeeRequests"),
    path('pendingCustomerRequests/', views.show_pending_customer_requests, name="pendingCustomerRequests"),
    url(r'^$', TemplateView.as_view(template_name="customer_edit_request_submitted.html"), 
        name='customer_edit_request_submitted'),
    url(r'^$', TemplateView.as_view(template_name="customer_request_already_exists.html"), 
        name='customer_request_already_exists'),
    path('technicalSupport/', views.technicalSupport, name='technicalSupport'),
    path('overrideRequests/', views.override_request, name='technicalSupport'),
    url(r'^$', TemplateView.as_view(template_name="employee_edit_request_submitted.html"),
        name='employee_edit_request_submitted'),
    url(r'^$', TemplateView.as_view(template_name="employee_request_already_exists.html"),
        name='employee_request_already_exists')
]
