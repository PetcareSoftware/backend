from django.shortcuts import render
from rest_framework import viewsets
from apps.stock.models import Insumo
from apps.stock.serializers import InsumoSerializer

# Create your views here.

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer