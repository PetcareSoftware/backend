from rest_framework import serializers
from django.utils import timezone
from apps.stock.models import Supply, SupplyBatch

class BatchCreateFromFrontendSerializer(serializers.Serializer):
    insumoId = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1) 
    batch = serializers.CharField(max_length=50)
    expirationDate = serializers.DateField()
    acquisitionCost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    details = serializers.CharField(required=False, allow_blank=True, default='')
    observations = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_expirationDate(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError("La fecha de vencimiento no puede ser pasada o igual a hoy.")
        return value

    def validate_insumoId(self, value):
        try:
            Supply.objects.get(id=value)
        except Supply.DoesNotExist:
            raise serializers.ValidationError("Insumo no encontrado.")
        return value

class BatchReadSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(source='lot_number')
    expirationDate = serializers.DateField(source='expiration_date')
    quantity = serializers.IntegerField(source='current_stock')
    supply_name = serializers.CharField(source='supply.name', read_only=True)
    supply_sku = serializers.CharField(source='supply.sku', read_only=True)

    class Meta:
        model = SupplyBatch
        fields = ['id', 'supply', 'supply_name', 'supply_sku', 'batch', 'expirationDate', 'quantity', 'initial_stock', 'acquisition_cost', 'created_at']

class AlertItemSerializer(serializers.Serializer):
    supply_id = serializers.UUIDField()
    supply_name = serializers.CharField()
    supply_sku = serializers.CharField()
    alert_type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    current_value = serializers.IntegerField()
    threshold_value = serializers.IntegerField(required=False)
    days_remaining = serializers.IntegerField(required=False)
    batch_id = serializers.UUIDField(required=False)
    lot_number = serializers.CharField(required=False)
