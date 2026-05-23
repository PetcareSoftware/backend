from django.conf import settings
from django.db import models


class Insumo(models.Model):
    nombre = models.CharField(max_length=150)
    stock_actual = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock_actual}"


class LogEntry(models.Model):
    """
    Modelo de auditoría para registrar eventos del sistema.
    Puede ser reubicado al módulo de Base de Datos cuando se requiera.
    """
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users_log_entries'
    )

    action = models.CharField(max_length=50, db_index=True)

    details = models.TextField(blank=True, default='')

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'action']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"