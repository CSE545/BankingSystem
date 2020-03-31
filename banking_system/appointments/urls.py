from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('schedule_appointment/', views.schedule_appointment, name="schedule_appointment"),
    path('view_appointments/', views.view_appointments, name="view_appointments"),
    path('cancel_appointment/', views.cancel_appointment, name="cancel_appointment"),
    path('get_taken_slots/', views.get_taken_slots, name="get_taken_slots"),
    path('view_app_requests/', views.view_app_requests, name="view_app_requests"),
    path('update_app_request/', views.update_app_request, name="update_app_request")
]
