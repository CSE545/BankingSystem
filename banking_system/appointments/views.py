from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from appointments.utility.handle_appointments import make_appointment
from appointments.models import Appointment
from django.http import HttpResponse

# Create your views here.
@login_required
def schedule_appointment(request):
    context = {}
    if request.POST:
        date = request.POST['date']
        time = request.POST['time']
        appointment_reason = request.POST['appointment_reason']
        appointment = make_appointment(request.user, date, time, appointment_reason)
        context['scheduled'] = True
        context['details'] = appointment
    else:
        active_appointments = Appointment.objects.filter(
            user=request.user,
            status='REQUESTED'
        ).count()
        if active_appointments > 0:
            context['active_appointments'] = True
        else:
            context['initial_view'] = True
    return render(request, 'appointments/schedule_appointment.html', context)


@login_required
def view_appointments(request):
    context = {}
    appointments = Appointment.objects.filter(
        user=request.user
    )
    context['appointments'] = {
        'headers': ['Appointment date', 'Appointment time', 'Reason', 'Created on', 'Status'],
        'details': []
    }
    for app in appointments:
        context['appointments']['details'].append([
            app.scheduled_date,
            app.scheduled_time,
            app.reason,
            app.created_at,
            app.status,
            app.app_id
        ])
    return render(request, 'appointments/view_appointment.html', context)


@login_required
def cancel_appointment(request):
    app_id = request.POST['app_id']
    Appointment.objects.filter(app_id=app_id).update(status='CANCELLED')
    return HttpResponse("Success")
