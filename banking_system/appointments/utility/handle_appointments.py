from appointments.models import Appointment


def make_appointment(user, date, time, appointment_reason):
    appointment = Appointment.objects.create(
        scheduled_date=date,
        scheduled_time=time,
        user=user,
        reason=appointment_reason
    )
    return appointment
