from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import Insumo
from .serializers import InsumoSerializer

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    @action(detail=True, methods=['post'])
    def descontar(self, request, pk=None):
        insumo = self.get_object()
        try:
            cantidad_str = request.data.get('cantidad', 0)
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor a cero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Insumo.objects.filter(pk=pk).update(stock_actual=F('stock_actual') - cantidad)
            return Response({'status': 'Stock actualizado con éxito'}, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response({'error': 'Cantidad no válida'}, status=status.HTTP_400_BAD_REQUEST)