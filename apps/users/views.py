from rest_framework import viewsets
from .models import Insumo
from .serializers import InsumoSerializer
from .permissions import EsTecnicoVeterinario # Tu nuevo permiso

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    
    # Aquí defines la autorización
    permission_classes = [EsTecnicoVeterinario]

    def get_queryset(self):
        """
        Personalización de la 'información concreta':
        El técnico solo ve insumos que no estén marcados como eliminados.
        """
        return Insumo.objects.filter(esta_activo=True)
    @action(detail=True, methods=['post'])
    def descontar(self, request, pk=None):
        insumo = self.get_object()
        cantidad = int(request.data.get('cantidad', 0))
        
        # Resta atómica: Protege la base de datos de errores de cálculo
        Insumo.objects.filter(pk=pk).update(stock_actual=F('stock_actual') - cantidad)
        
        return Response({'status': 'Stock actualizado con éxito'})