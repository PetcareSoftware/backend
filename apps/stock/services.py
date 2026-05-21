from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.stock.models import MedicalSupply, SupplyBatch

def consume_supply_fifo(supply_id, quantity_to_deduct):
    """
    Descuenta unidades de stock de un insumo médico aplicando lógica FIFO estricta.
    Implementa select_for_update para evitar condiciones de carrera concurrentes.
    Soporta el escenario CU-17.
    """
    if quantity_to_deduct <= 0:
        raise ValidationError({"error": "The quantity to deduct must be a positive integer."})

    with transaction.atomic():
        try:
            supply = MedicalSupply.objects.select_for_update().get(pk=supply_id)
        except MedicalSupply.DoesNotExist:
            raise ValidationError({"error": f"Medical supply with ID {supply_id} does not exist."})

        if supply.current_stock < quantity_to_deduct:
            raise ValidationError({
                "error": f"Insufficient stock for {supply.supply_name}. "
                         f"Required: {quantity_to_deduct}, Available: {supply.current_stock}"
            })

        active_batches = SupplyBatch.objects.filter(
            id_supply=supply,
            quantity_available__gt=0,
            expiration_date__gt=timezone.now().date()
        ).order_by('expiration_date')

        total_available = sum(b.quantity_available for b in active_batches)

        if total_available < quantity_to_deduct:
            raise ValidationError({
                "error": f"Insufficient stock from non-expired batches for {supply.supply_name}. "
                         f"Available: {total_available}."
            })

        remaining = quantity_to_deduct

        for batch in active_batches:
            if remaining <= 0:
                break

            if batch.quantity_available >= remaining:
                batch.quantity_available -= remaining
                batch.save()
                remaining = 0
            else:
                remaining -= batch.quantity_available
                batch.quantity_available = 0
                batch.save()

        supply.current_stock -= quantity_to_deduct
        supply.save()

        return supply
