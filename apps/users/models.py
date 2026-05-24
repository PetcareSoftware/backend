from django.db import models
from django.contrib.auth import get_user_model

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
