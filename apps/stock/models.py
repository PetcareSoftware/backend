from django.db import models

class Insumo(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre del insumo")
    current_stock = models.IntegerField(default=0, verbose_name="Existencias físicas reales disponibles")
    expiration_date = models.DateField(verbose_name="Fecha de vencimiento")
    min_stock_alert = models.IntegerField(default=0, verbose_name="Umbral mínimo de almacén para disparar alertas")

    @property
    def necesita_reposicion(self):
        return self.current_stock <= self.min_stock_alert

    def __str__(self):
        return self.name
