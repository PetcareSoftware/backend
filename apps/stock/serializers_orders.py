# apps/stock/serializers_orders.py
from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

from apps.stock.models import (
    PurchaseOrder, PurchaseOrderItem, Supply, Supplier, SupplyBatch,
)


class PurchaseOrderItemReadSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura para ítems de orden."""
    supply_name = serializers.CharField(source='supply.name', read_only=True)
    supply_sku = serializers.CharField(source='supply.sku', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'supply', 'supply_name', 'supply_sku',
            'quantity_requested', 'unit_cost',
        ]
        read_only_fields = ['id']


class PurchaseOrderItemCreateSerializer(serializers.Serializer):
    insumoId = serializers.UUIDField()
    nombre = serializers.CharField(required=False)  # Ignorado, solo display
    cantidad = serializers.IntegerField(min_value=1)
    costoUnitario = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.01')
    )

    def validate_insumoId(self, value):
        if not Supply.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                f"El insumo con ID '{value}' no existe."
            )
        return value


class PurchaseOrderCreateSerializer(serializers.Serializer):
    proveedor = serializers.UUIDField()
    items = PurchaseOrderItemCreateSerializer(many=True, min_length=1)

    def validate_proveedor(self, value):
        if not Supplier.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                f"El proveedor con ID '{value}' no existe."
            )
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "La orden debe contener al menos un ítem."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        supplier = Supplier.objects.get(pk=validated_data['proveedor'])

        total_cost = sum(
            Decimal(str(item['cantidad'])) * item['costoUnitario']
            for item in items_data
        )

        order = PurchaseOrder.objects.create(
            supplier=supplier,
            total_cost=total_cost,
            status='REQUESTED',
        )

        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                order=order,
                supply_id=item_data['insumoId'],
                quantity_requested=item_data['cantidad'],
                unit_cost=item_data['costoUnitario'],
            )

        return order


class PurchaseOrderReadSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemReadSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(
        source='supplier.name', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'manager',
            'total_cost', 'status', 'status_display',
            'created_at', 'updated_at', 'items',
        ]


class PurchaseOrderApproveSerializer(serializers.Serializer):
    pass


class ReceiveItemSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    lot_number = serializers.CharField(max_length=50)
    expiration_date = serializers.DateField()
    quantity_received = serializers.IntegerField(min_value=1)

    def validate_item_id(self, value):
        if not PurchaseOrderItem.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                f"El ítem con ID '{value}' no existe."
            )
        return value


class PurchaseOrderReceiveSerializer(serializers.Serializer):
    received_items = ReceiveItemSerializer(many=True, min_length=1)

    def validate_received_items(self, value):
        order = self.context.get('order')
        if order:
            order_item_ids = set(
                str(item.id) for item in order.items.all()
            )
            received_item_ids = set(
                str(item['item_id']) for item in value
            )
            missing = order_item_ids - received_item_ids
            if missing:
                raise serializers.ValidationError(
                    f"Faltan datos de recepción para los ítems: {missing}"
                )
        return value


class PurchaseOrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)