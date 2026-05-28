from rest_framework import serializers
from .models import Notification, NotificationLog


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ['id', 'channel', 'status', 'detail', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    logs = NotificationLogSerializer(many=True, read_only=True)
    body = serializers.CharField(source='message', read_only=True)
    type = serializers.CharField(source='notification_type', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'body',
            'notification_type',
            'type',
            'is_read',
            'created_at',
            'read_at',
            'logs',
        ]
