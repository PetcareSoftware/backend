from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Supply(models.Model):
    name = models.CharField(max_length=150, verbose_name='nombre')
    current_stock = models.IntegerField(default=0, verbose_name='stock actual')

    class Meta:
        verbose_name = 'insumo'
        verbose_name_plural = 'insumos'

    def __str__(self):
        return f"{self.name} - Stock: {self.current_stock}"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='usuario')
    action = models.CharField(max_length=10, verbose_name='acción') 
    path = models.CharField(max_length=255, verbose_name='ruta')  
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='fecha')
    details = models.TextField(null=True, blank=True, verbose_name='detalles') 

    class Meta:
        verbose_name = 'registro de auditoría'
        verbose_name_plural = 'registros de auditoría'

    def __str__(self):
        nombre_usuario = self.user.email if self.user else "Anónimo"
        return f"{nombre_usuario} hizo {self.action} en {self.path} a las {self.timestamp}"


class SystemGroups:
    """
    Clase para obtener o crear los grupos de forma segura
    sin romper las migraciones de Django.
    """
    @property
    def owner(self):
        group, _ = Group.objects.get_or_create(name="owner")
        return group

    @property
    def receptionist(self):
        group, _ = Group.objects.get_or_create(name="receptionist")
        return group

groups = SystemGroups()