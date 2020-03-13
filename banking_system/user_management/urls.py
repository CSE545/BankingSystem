from django.contrib.auth.views import LogoutView
from django.urls import path
from user_management.views import trans_create, transaction_view, trans_list_view

from . import views

app_name = 'user_management'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', views.view_profile, name="view_profile"),
    path('profile/edit/', views.edit_profile, name="edit_profile"),
    path('trans/create', trans_create, name="trans_create"),
    path('trans/list/view/<int:id>/', transaction_view, name="trans_view"),
    path('trans/list/', trans_list_view, name="list")
]
