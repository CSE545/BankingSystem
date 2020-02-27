from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('update/', views.update_user, name="user_update")
]
