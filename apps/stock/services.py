from django.db import transaction
from django.core.exceptions import ValidationError
from apps.stock.models import SupplyBatch, ConsultationSupply

def consume_supply_securely(batch_id,consultation_ide,quantity):
    """
    Control de concurrencia transaccional (ACID) para descontar inventario 
    y registrar su uso en una consulta de forma atómica.
    """
    with transaction.atomic():
        try:
            batch =SupplyBatch.objects.select_for_update().get(id = batch_id)
        except SupplyBatch.DoesNotExist:
            raise ValidationError(f"El lote de insumo con id {batch_id} no existe.")
        if batch.current_stock < quantity:
            raise ValidationError(
                f"Error de inventario: Stock insuficiente en el lote {batch.lot_number}. "
                f"Se pidieron {quantity}, pero solo quedan {batch.current_stock} disponibles."
            )
        batch.current_stock -= quantity
        batch.save()
        register = ConsultationSupply.objects.create(
            consultation_id = consultation_ide,
            batch = batch_id,
            quantity_used = quantity
        )
    return register
