from datetime import timedelta
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Appointment
from .tasks import request_attendance_confirmation, send_appointment_reminder


def _eta_or_now(when):
    return when if when > timezone.now() else timezone.now()


def _safe_apply_async(task, appointment_id, eta):
    try:
        task.apply_async(args=[str(appointment_id)], eta=eta)
    except Exception:
        # No romper la transacción HTTP si Celery/Redis no está disponible.
        pass


@receiver(post_save, sender=Appointment)
def on_appointment_created(sender, instance, created, **kwargs):
    if not created:
        return
    reminder_eta = _eta_or_now(instance.scheduled_at - timedelta(hours=24))
    confirmation_eta = _eta_or_now(instance.scheduled_at - timedelta(hours=48))
    transaction.on_commit(lambda: _safe_apply_async(send_appointment_reminder, instance.id, reminder_eta))
    transaction.on_commit(lambda: _safe_apply_async(request_attendance_confirmation, instance.id, confirmation_eta))
