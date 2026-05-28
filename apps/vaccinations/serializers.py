from rest_framework import serializers
from .models import VaccinationEvent, VaccinationPlan, VaccinationPlanItem


class VaccinationPlanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationPlanItem
        fields = ['id', 'vaccine_name', 'scheduled_date', 'supply_id', 'notes']
        read_only_fields = ['id']



class VaccinationPlanCreateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    items = VaccinationPlanItemSerializer(many=True, required=False)


class VaccinationPlanSerializer(serializers.ModelSerializer):
    items = VaccinationPlanItemSerializer(many=True, read_only=True)

    class Meta:
        model = VaccinationPlan
        fields = ['id', 'patient_id', 'created_by_id', 'is_active', 'notes', 'created_at', 'items']
        read_only_fields = ['id', 'patient_id', 'created_by_id', 'is_active', 'created_at']


class VaccinationEventSerializer(serializers.ModelSerializer):
    plan_item_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = VaccinationEvent
        fields = ['id', 'patient_id', 'plan_item_id', 'created_by_id', 'vaccine_name', 'applied_date', 'batch_number', 'dose', 'next_due_date', 'supply_id', 'quantity_used', 'sync_status', 'created_at']
        read_only_fields = ['id', 'patient_id', 'created_by_id', 'sync_status', 'created_at']

    def validate(self, attrs):
        if attrs.get('supply_id') and not attrs.get('quantity_used'):
            raise serializers.ValidationError({'quantity_used': ['Requerido si se especifica supply_id.']})
        return attrs
