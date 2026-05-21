from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MedicalSupply, SupplyBatch
from .serializers import MedicalSupplySerializer, SupplyBatchSerializer
from .services import consume_supply_fifo

class MedicalSupplyViewSet(viewsets.ModelViewSet):
    queryset = MedicalSupply.objects.all()
    serializer_class = MedicalSupplySerializer
    permission_classes = [IsAuthenticated]


class SupplyBatchViewSet(viewsets.ModelViewSet):
    queryset = SupplyBatch.objects.all()
    serializer_class = SupplyBatchSerializer
    permission_classes = [IsAuthenticated]


class StockConsumptionViewSet(viewsets.ViewSet):
    """
    Endpoint transaccional unificado para el descuento de insumos en lotes.
    Soporta el escenario CU-17.
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        # Payload esperado: {"supply_id": int, "quantity": int}
        supply_id = request.data.get('supply_id')
        quantity = request.data.get('quantity')

        if not supply_id or quantity is None:
            return Response(
                {"error": "Los campos 'supply_id' y 'quantity' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "El campo 'quantity' debe ser un número entero mayor a cero."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se invoca la lógica de negocio FIFO
        try:
            updated_supply = consume_supply_fifo(supply_id, quantity)
        except Exception as e:
            # Capturamos errores de DRF o validación de stock
            error_detail = e.detail if hasattr(e, 'detail') else str(e)
            return Response(error_detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(
            {
                "message": "Consumo de inventario registrado exitosamente.",
                "supply_id": updated_supply.id_supply,
                "current_stock": updated_supply.current_stock
            },
            status=status.HTTP_200_OK
        )