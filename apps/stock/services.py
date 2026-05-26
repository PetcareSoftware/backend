from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.stock.models import Supply, SupplyBatch, ConsultationSupply

@transaction.atomic
def consume_supply_fifo(supply_id, quantity, consultation_id=None):
    """
    Consume stock de un insumo médico utilizando el algoritmo FIFO
    (First Expiry First Out) basado en la fecha de vencimiento.
    """
    if quantity <= 0:
        raise ValidationError("La cantidad a consumir debe ser mayor que cero.")

    try:
        supply = Supply.objects.select_for_update().get(id=supply_id)
    except (Supply.DoesNotExist, ValueError):
        raise ValidationError("Insumo no encontrado o ID inválido.")

    batches = SupplyBatch.objects.select_for_update().filter(
        supply=supply,
        expiration_date__gt=timezone.now().date(),
        current_stock__gt=0
    ).order_by('expiration_date')

    total_available = sum(b.current_stock for b in batches)
    if total_available < quantity:
        raise ValidationError(
            f"Stock insuficiente para {supply.name}. Requerido: {quantity}, Disponible: {total_available}."
        )

    remaining_to_consume = quantity
    for batch in batches:
        if remaining_to_consume <= 0:
            break
        take = min(batch.current_stock, remaining_to_consume)
        batch.current_stock -= take
        batch.save()
        if consultation_id:
            ConsultationSupply.objects.create(
                consultation_id=consultation_id,
                batch=batch,
                quantity_used=take
            )
        remaining_to_consume -= take

    return supply
