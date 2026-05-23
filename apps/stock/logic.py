# apps/stock/logic.py
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.stock.models import Supply, SupplyBatch

@transaction.atomic
def descontar_stock_insumo(insumo_id, cantidad):
    """
    Descuenta la cantidad solicitada de un insumo médico de forma atómica.
    
    Aplica select_for_update() para bloquear las filas en la base de datos 
    y evitar condiciones de carrera (concurrencia) en la clínica.
    """
    # 1. Buscar el insumo bloqueando la fila con select_for_update()
    try:
        insumo = Supply.objects.select_for_update().get(id=insumo_id)
    except Supply.DoesNotExist:
        raise ValidationError({"error": f"El insumo con ID {insumo_id} no existe en el sistema."})

    # 2. Obtener los lotes activos con stock disponible, ordenados por vencimiento (FIFO)
    # También bloqueamos los lotes que se van a modificar concurrentemente
    lotes = SupplyBatch.objects.select_for_update().filter(
        supply=insumo,
        current_stock__gt=0,
        expiration_date__gte=timezone.now().date()
    ).order_by('expiration_date')

    # 3. Validar si la suma de todos los lotes es suficiente
    total_disponible = sum(lote.current_stock for lote in lotes)
    if total_disponible < cantidad:
        # Lanzamos ValidationError con la clave 'error' para que el controlador responda HTTP 400
        raise ValidationError({
            "error": f"Stock insuficiente para '{insumo.name}'. Disponible: {total_disponible}, Requerido: {cantidad}."
        })

    # 4. Algoritmo de descuento lote por lote
    por_descontar = cantidad
    for lote in lotes:
        if por_descontar <= 0:
            break
        
        if lote.current_stock >= por_descontar:
            lote.current_stock -= por_descontar
            por_descontar = 0
        else:
            por_descontar -= lote.current_stock
            lote.current_stock = 0
        
        # Guardar los cambios de cada lote dentro de la transacción
        lote.save()

    return insumo