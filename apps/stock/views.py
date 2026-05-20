from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
import logging

from .models import SupplyBatch, ConsultationSupply
from .serializers import SupplyBatchSerializer
from .logic import descontar_stock_lote

logger = logging.getLogger(__name__)

class SupplyBatchViewSet(viewsets.ModelViewSet):
    queryset = SupplyBatch.objects.all()
    serializer_class = SupplyBatchSerializer

    @action(detail=True, methods=['post'], url_path='consumir')
    def consumir(self, request, pk=None):
        lote = self.get_object()
        cantidad = request.data.get('cantidad')
        consultation_id = request.data.get('consultation_id')

        if cantidad is None:
            return Response(
                {'error': 'El campo "cantidad" es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {'error': 'La "cantidad" debe ser un número entero mayor a cero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lote_actualizado, consumo_registro = descontar_stock_lote(
                batch_id=lote.id,
                cantidad=cantidad,
                consultation_id=consultation_id
            )
        except DRFValidationError as e:
            error_msg = e.detail.get('error', str(e)) if hasattr(e, 'detail') else str(e)
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al descontar lote {lote.id}: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(lote_actualizado)
        return Response(
            {
                'mensaje': 'Consumo registrado exitosamente',
                'lote': serializer.data,
                'consumo_id': str(consumo_registro.id) if consumo_registro else None
            },
            status=status.HTTP_200_OK
        )
