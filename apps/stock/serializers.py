# apps/stock/serializers.py
from rest_framework import serializers
from apps.stock.models import PurchaseOrder, PurchaseOrderItem, Supply, Supplier

class PurchaseOrderItemReadSerializer(serializers.ModelSerializer):
    """Muestra los detalles legibles de un ítem dentro de una orden."""
    supply_name = serializers.CharField(source='supply.name', read_only=True)
    supply_sku = serializers.CharField(source='supply.sku', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'supply', 'supply_name', 'supply_sku', 'quantity_requested', 'unit_cost']

class PurchaseOrderItemWriteSerializer(serializers.Serializer):
    """Valida los datos crudos que vienen del componente Interface.vue."""
    insumoId = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

class PurchaseOrderReadSerializer(serializers.ModelSerializer):
    """Serializador para responder con el estado completo de la orden."""
    items = PurchaseOrderItemReadSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'supplier_name', 'total_cost', 'status', 'status_display', 'items', 'created_at', 'updated_at']

class PurchaseOrderCreateSerializer(serializers.Serializer):
    """Valida la creación de la orden con múltiples ítems."""
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    items = PurchaseOrderItemWriteSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un insumo en la orden.")
        return value