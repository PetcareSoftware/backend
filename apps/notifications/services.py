from django.utils import timezone
from .models import Notification, NotificationLog


class NotificationService:
    @staticmethod
    def create(*, user, title, message, notification_type=Notification.Type.GENERAL):
        notification = Notification.objects.create(user=user, title=title, message=message, notification_type=notification_type)
        NotificationLog.objects.create(notification=notification, channel='in_app', status=NotificationLog.Status.SENT)
        return notification

    @staticmethod
    def mark_read(*, actor, notification):
        if str(notification.user_id) != str(actor.id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('No puedes marcar notificaciones de otro usuario.')
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
        return notification

    @staticmethod
    def log_task_failure(channel, detail, appointment_id=None, notification=None):
        return NotificationLog.objects.create(
            notification=notification,
            channel=channel,
            status=NotificationLog.Status.FAILED,
            detail=detail,
            appointment_id=appointment_id,
        )
