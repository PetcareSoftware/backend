from django.conf import settings
from django.db import models


class Owner(models.Model):
    # ERD estricto: owners.user_id es PK y FK a users.id.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, db_column='user_id', on_delete=models.CASCADE, related_name='owner_profile')
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dni = models.CharField(max_length=20, unique=True, blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'owners'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'.strip() or self.user.email

    def pets_appointments(self):
        from apps.appointments.models import Appointment
        return Appointment.objects.filter(pet__owner=self).order_by('-scheduled_at')
