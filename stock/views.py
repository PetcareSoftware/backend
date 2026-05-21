from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.stock.models import MedicalSupply
from apps.stock.serializers import MedicalSupplySerializer

class MedicalSupplyViewSet(viewsets.ModelViewSet):
    queryset = MedicalSupply.objects.all()
    serializer_class = MedicalSupplySerializer
    permission_classes = [IsAuthenticated]