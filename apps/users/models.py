from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
user = get_user_model()

class Insumo(models.Model):
    nombre = models.CharField(max_length=150)
    stock_actual = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock_actual}"

class RegistroAuditoria(models.Model):
    usuario = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=10) 
    ruta = models.CharField(max_length=255)  
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(null=True, blank=True) 

    def __str__(self):
        nombre = self.usuario.email if self.usuario else "Anónimo"
        return f"{nombre} hizo {self.accion} en {self.ruta} a las {self.fecha}"


class SystemGroups:
    """
    Clase para obtener o crear los grupos de forma segura 
    sin romper las migraciones de Django.
    """
    @property
    def owner(self):
        grupo, _ = Group.objects.get_or_create(name="owner")
        return grupo

    @property
    def receptionist(self):
        grupo, _ = Group.objects.get_or_create(name="receptionist")
        return grupo
groups = SystemGroups()