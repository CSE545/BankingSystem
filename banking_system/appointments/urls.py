from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('schedule_appointment/', views.schedule_appointment, name="schedule_appointment"),
    path('view_appointments/', views.view_appointments, name="view_appointments"),
    path('cancel_appointment/', views.cancel_appointment, name="cancel_appointment"),
]
