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
