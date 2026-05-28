import uuid
from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        REMINDER = 'REMINDER', 'Recordatorio de cita'
        CONFIRMATION = 'CONFIRMATION', 'Confirmación de asistencia'
        ALERT = 'ALERT', 'Alerta'
        STATUS_CHANGE = 'STATUS_CHANGE', 'Cambio de estado'
        GENERAL = 'GENERAL', 'General'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='user_id', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=Type.choices, default=Type.GENERAL)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class NotificationLog(models.Model):
    class Status(models.TextChoices):
        SENT = 'SENT', 'Enviada'
        FAILED = 'FAILED', 'Fallida'
        PENDING = 'PENDING', 'Pendiente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, db_column='notification_id', on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    channel = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    detail = models.TextField(blank=True, null=True)
    appointment_id = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_logs'
