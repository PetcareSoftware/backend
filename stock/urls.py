from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.stock.views import InsumoViewSet

# Configuración del Router para el módulo de inventario
router = DefaultRouter()
router.register(r'insumos', InsumoViewSet, basename='insumos')

urlpatterns = [
    path('api/', include("apps.stock.urls")),
]