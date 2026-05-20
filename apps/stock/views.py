from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
import logging

from .models import Insumo
from .serializers import InsumoSerializer
from .logic import descontar_stock_insumo

logger = logging.getLogger(__name__)


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

    @action(detail=True, methods=['post'], url_path='consumir')
    def consumir(self, request, pk=None):
        """
        Endpoint personalizado para descontar stock de un insumo específico.
        Payload: {"cantidad": <int>}
        """
        insumo = self.get_object()
        cantidad = request.data.get('cantidad')

        # Validaciones del payload
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

        # Llamada a la lógica transaccional de Freddy
        try:
            insumo_actualizado = descontar_stock_insumo(insumo.id, cantidad)
        except DRFValidationError as e:
            error_msg = e.detail.get('error', str(e)) if hasattr(e, 'detail') else str(e)
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al descontar insumo {insumo.id}: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(insumo_actualizado)
        return Response(
            {
                'mensaje': 'Consumo registrado exitosamente',
                'insumo': serializer.data
            },
            status=status.HTTP_200_OK
        )
