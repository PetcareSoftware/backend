from rest_framework import serializers
from apps.stock.models import MedicalSupply, SupplyBatch

class MedicalSupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalSupply
        fields = '__all__'

class SupplyBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyBatch
        fields = '__all__'
