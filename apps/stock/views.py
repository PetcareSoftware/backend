from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.stock.models import MedicalSupply
from apps.stock.serializers import MedicalSupplySerializer
from apps.stock.services import consume_supply_fifo

class MedicalSupplyViewSet(viewsets.ModelViewSet):
    queryset = MedicalSupply.objects.all()
    serializer_class = MedicalSupplySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='consumir')
    def consumir(self, request, pk=None):
        """
        Endpoint para consumir stock de un insumo médico (FIFO automático).
        Payload esperado: {"quantity": <int>}
        """
        supply = self.get_object()
        quantity = request.data.get('quantity')

        if quantity is None:
            return Response(
                {"error": "The 'quantity' field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "The 'quantity' must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_supply = consume_supply_fifo(supply.id, quantity)
        except Exception as e:
            error_detail = e.detail if hasattr(e, 'detail') else str(e)
            return Response(
                {"error": error_detail},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        return Response(
            {
                "message": "Stock consumption registered successfully.",
                "supply_id": updated_supply.id,
                "current_stock": updated_supply.current_stock
            },
            status=status.HTTP_200_OK
        )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.stock.services import consume_supply_fifo

class InventoryConsumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        supply_id = request.data.get('supply_id')
        quantity = request.data.get('quantity')
        consultation_id = request.data.get('consultation_id')

        if not supply_id or not quantity:
            return Response(
                {"error": "Los campos 'supply_id' y 'quantity' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response(
                {"error": "La cantidad debe ser un número entero válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_supply = consume_supply_fifo(supply_id, quantity, consultation_id)
            return Response({
                "message": "Consumo FIFO registrado con éxito.",
                "supply_id": updated_supply.id,
                "name": updated_supply.name
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
