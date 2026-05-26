from rest_framework import serializers
from django.db.models import Sum
from django.utils import timezone
from apps.stock.models import Supply, SupplyBatch, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Supplier (Proveedor).
    Expone todos los campos directamente sin transformación.
    """
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_name',
            'phone', 'email', 'address'
        ]
        read_only_fields = ['id']


class SupplyBatchSerializer(serializers.ModelSerializer):
    """
    Serializador para lotes individuales de un insumo.
    Mapea los nombres de campo del backend a los del frontend:
      - lot_number    → batch
      - expiration_date → expirationDate
      - current_stock  → quantity
    """
    batch = serializers.CharField(source='lot_number', read_only=True)
    expirationDate = serializers.DateField(source='expiration_date', read_only=True)
    quantity = serializers.IntegerField(source='current_stock', read_only=True)

    class Meta:
        model = SupplyBatch
        fields = [
            'id', 'batch', 'expirationDate',
            'quantity', 'acquisition_cost'
        ]
        read_only_fields = ['id']


class SupplyBatchWriteSerializer(serializers.ModelSerializer):
    """
    Serializador de ESCRITURA para crear/actualizar lotes.
    Utiliza los nombres originales de la DB (lot_number, expiration_date, etc.)
    """
    class Meta:
        model = SupplyBatch
        fields = [
            'id', 'supply', 'lot_number', 'expiration_date',
            'initial_stock', 'current_stock', 'acquisition_cost'
        ]
        read_only_fields = ['id', 'created_at']


class SupplySerializer(serializers.ModelSerializer):
    """
    Serializador principal para el catálogo de insumos.
    Implementa campos calculados dinámicamente para el frontend:
      - quantity  = suma de current_stock de lotes vigentes
      - unitCost  = acquisition_cost del lote más reciente
      - umbral    = min_stock_alert
      - batches   = lista de lotes activos mapeados al formato frontend
    """
    quantity = serializers.SerializerMethodField()
    unitCost = serializers.SerializerMethodField()
    umbral = serializers.IntegerField(source='min_stock_alert')
    batches = serializers.SerializerMethodField()

    class Meta:
        model = Supply
        fields = [
            'id', 'sku', 'name', 'description',
            'category', 'umbral',
            'quantity', 'unitCost', 'batches'
        ]
        read_only_fields = ['id']

    def get_quantity(self, obj):
        """
        Calcula el stock global disponible del insumo.
        Suma current_stock de todos los lotes cuya fecha de
        caducidad sea posterior al día de hoy.
        """
        today = timezone.now().date()
        active_batches = obj.batches.filter(
            expiration_date__gt=today,
            current_stock__gt=0
        )
        total = active_batches.aggregate(
            total=Sum('current_stock')
        )['total']
        return total if total is not None else 0

    def get_unitCost(self, obj):
        """
        Obtiene el costo unitario de referencia del insumo.
        Toma el acquisition_cost del lote más reciente (por fecha de creación).
        Si no hay lotes, devuelve 0.00.
        """
        latest_batch = obj.batches.order_by('-created_at').first()
        if latest_batch:
            return float(latest_batch.acquisition_cost)
        return 0.00

    def get_batches(self, obj):
        """
        Retorna la lista de lotes activos (con stock > 0 y no vencidos)
        ordenados por fecha de caducidad ascendente (los más próximos a
        vencer primero, que es el orden FIFO).
        """
        today = timezone.now().date()
        active_batches = obj.batches.filter(
            expiration_date__gt=today,
            current_stock__gt=0
        ).order_by('expiration_date')
        return SupplyBatchSerializer(active_batches, many=True).data


class SupplyWriteSerializer(serializers.ModelSerializer):
    """
    Serializador de ESCRITURA para crear/actualizar insumos.
    Acepta los nombres nativos de la DB (min_stock_alert, etc.)
    sin los campos calculados.
    """
    class Meta:
        model = Supply
        fields = [
            'id', 'sku', 'name', 'description',
            'category', 'min_stock_alert'
        ]
        read_only_fields = ['id']