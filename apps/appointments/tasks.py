from celery import shared_task
from apps.notifications.services import NotificationService
from .models import Appointment


SKIP_STATUSES = {Appointment.Status.CANCELLED, Appointment.Status.COMPLETED}


@shared_task
def send_appointment_reminder(appointment_id):
    try:
        appointment = Appointment.objects.select_related('pet__owner__user', 'slot').get(id=appointment_id)
        if appointment.status in SKIP_STATUSES:
            return None
        return str(NotificationService.create(
            user=appointment.pet.owner.user,
            title='Recordatorio de cita',
            message=f'Tienes una cita para {appointment.pet.name} el {appointment.slot.date} a las {appointment.slot.start_time}.',
            notification_type='REMINDER',
        ).id)
    except Exception as exc:
        NotificationService.log_task_failure('REMINDER', str(exc), appointment_id=appointment_id)
        return None


@shared_task
def request_attendance_confirmation(appointment_id):
    try:
        appointment = Appointment.objects.select_related('pet__owner__user', 'slot').get(id=appointment_id)
        if appointment.status in SKIP_STATUSES:
            return None
        return str(NotificationService.create(
            user=appointment.pet.owner.user,
            title='Confirma tu asistencia',
            message=f'Confirma la asistencia de {appointment.pet.name} a su cita.',
            notification_type='CONFIRMATION',
        ).id)
    except Exception as exc:
        NotificationService.log_task_failure('CONFIRMATION', str(exc), appointment_id=appointment_id)
        return None
