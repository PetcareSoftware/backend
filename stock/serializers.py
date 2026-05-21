from rest_framework import serializers
from apps.stock.models import MedicalSupply

class MedicalSupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalSupply
        fields = '__all__'