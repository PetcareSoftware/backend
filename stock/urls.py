# apps/stock/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.stock.views import MedicalSupplyViewSet, SupplyBatchViewSet

# Configuración del router automático de DRF
router = DefaultRouter()
router.register(r'supplies', MedicalSupplyViewSet, basename='supplies')
router.register(r'batches', SupplyBatchViewSet, basename='batches')

urlpatterns = [
    path('', include(router.urls)),
]