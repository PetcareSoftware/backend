from django.db import models

class Insumo(models.Model):
    nombre = models.CharField(max_length=150)
    stock_actual = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock_actual}"