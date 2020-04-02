from django.db import models
from user_management.models import User
# Create your models here.

REQUEST_STATUS = (
    ("REQUESTED", "REQUESTED"),
    ("SCHEDULED", "SCHEDULED"),
    ("DENIED", "DENIED"),
    ("CANCELLED", "CANCELLED")
)


class Appointment(models.Model):
    app_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.CharField(max_length=10)
    scheduled_time = models.CharField(max_length=10)
    user = models.ForeignKey(
        User, default=None, on_delete=models.CASCADE, related_name='userIdAppointment')
    status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS,
        default='REQUESTED'
    )
    reason = models.CharField(max_length=100, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Appointment, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Appointment Id: {0},  Status {1},  \
                User: {2}" \
                .format(self.app_id, self.status,
                        self.user.first_name + " " + self.user.last_name)
