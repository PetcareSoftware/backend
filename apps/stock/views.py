# apps/stock/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.stock.models import Supply, Supplier
from apps.stock.serializers import (
    SupplySerializer,
    SupplyWriteSerializer,
    SupplierSerializer,
)

class SupplyViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD completo para el catálogo maestro de insumos.
    Endpoints generados automáticamente:
      GET    /api/v1/inventory/supplies/          → Listar todos los insumos
      POST   /api/v1/inventory/supplies/          → Crear un insumo nuevo
      GET    /api/v1/inventory/supplies/<uuid>/    → Detalle de un insumo
      PUT    /api/v1/inventory/supplies/<uuid>/    → Actualizar un insumo
      PATCH  /api/v1/inventory/supplies/<uuid>/    → Actualización parcial
      DELETE /api/v1/inventory/supplies/<uuid>/    → Eliminar un insumo
    """
    queryset = Supply.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Utiliza el serializador de lectura (con campos calculados)
        para GET y el de escritura (campos nativos) para POST/PUT/PATCH.
        """
        if self.action in ['list', 'retrieve']:
            return SupplySerializer
        return SupplyWriteSerializer

    def list(self, request, *args, **kwargs):
        """
        Lista todos los insumos con sus campos calculados.
        El frontend (InventoryCatalog.vue) consume este endpoint
        para mostrar la tabla de inventario.
        """
        queryset = self.get_queryset().prefetch_related('batches')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Detalle de un insumo individual con todos sus lotes activos.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD completo para proveedores.
    Endpoints generados automáticamente:
      GET    /api/v1/inventory/suppliers/          → Listar proveedores
      POST   /api/v1/inventory/suppliers/          → Crear proveedor
      GET    /api/v1/inventory/suppliers/<uuid>/    → Detalle de proveedor
      PUT    /api/v1/inventory/suppliers/<uuid>/    → Actualizar proveedor
      PATCH  /api/v1/inventory/suppliers/<uuid>/    → Actualización parcial
      DELETE /api/v1/inventory/suppliers/<uuid>/    → Eliminar proveedor
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]