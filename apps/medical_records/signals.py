from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.appointments.models import Appointment
from .models import Consultation


@receiver(post_save, sender=Consultation)
def on_consultation_created(sender, instance, created, **kwargs):
    if created and instance.appointment.status != Appointment.Status.COMPLETED:
        instance.appointment.status = Appointment.Status.COMPLETED
        instance.appointment.save(update_fields=['status'])
