from celery import shared_task
from django.utils import timezone
from apps.appointments.models import Appointment
from apps.notifications.services import NotificationService


@shared_task
def send_due_appointment_reminders():
    # Tarea periódica opcional de Celery Beat: recordatorios para citas futuras no canceladas.
    upcoming = Appointment.objects.select_related('pet__owner__user', 'slot').filter(
        status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED],
        scheduled_at__gte=timezone.now(),
    )[:100]
    count = 0
    for appointment in upcoming:
        NotificationService.create(
            user=appointment.pet.owner.user,
            title='Recordatorio de cita',
            message=f'Cita pendiente para {appointment.pet.name}.',
            notification_type='REMINDER',
        )
        count += 1
    return count
