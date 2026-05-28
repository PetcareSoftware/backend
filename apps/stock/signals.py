from django.dispatch import Signal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import SupplyBatch

@receiver(post_save, sender=SupplyBatch)
def check_minimum_stock(sender, instance, **kwargs):
    supply = instance.supply
    resultado = supply.batches.aggregate(total_stock=Sum('current_stock'))
    stock_total = resultado['total_stock'] or 0
    if stock_total <= supply.min_stock_alert:
        mensaje = (
            f"ALERTA DE STOCK: El insumo '{supply.name}' (SKU: {supply.sku}) "
            f"ha alcanzado el stock mínimo. "
            f"Disponible: {stock_total} | Mínimo permitido: {supply.min_stock_alert}"
        )
        print(mensaje)
