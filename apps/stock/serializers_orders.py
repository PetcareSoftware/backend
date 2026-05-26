# apps/stock/serializers_orders.py
from rest_framework import serializers
from apps.stock.models import PurchaseOrder, PurchaseOrderItem

class PurchaseOrderItemReadSerializer(serializers.ModelSerializer):
    supply_name = serializers.CharField(source='supply.name', read_only=True)
    supply_sku = serializers.CharField(source='supply.sku', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'supply', 'supply_name', 'supply_sku', 'quantity_requested', 'unit_cost']

class PurchaseOrderItemWriteSerializer(serializers.Serializer):
    insumoId = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

class PurchaseOrderReadSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemReadSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'supplier_name', 'total_cost', 'status', 'status_display', 'items', 'created_at', 'updated_at']

class PurchaseOrderCreateSerializer(serializers.Serializer):
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    manager_id = serializers.UUIDField(required=True) 
    items = PurchaseOrderItemWriteSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un insumo en la orden.")
        return value