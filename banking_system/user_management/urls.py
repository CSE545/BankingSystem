from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'user_management'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', views.view_profile, name="view_profile"),
    path('transfers/', views.transfers, name="transfers"),
    path('pendingFundTransfers/', views.pendingFundTransfers, name="pendingFundTransfers"),
    path('profile/edit/', views.edit_profile, name="edit_profile"),
    path('pendingEmployeeRequests/', views.show_pending_employee_requests, name="pendingEmployeeRequests")
]
