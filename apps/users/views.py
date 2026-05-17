# Asegúrate de tener estas importaciones arriba
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import Insumo  # O como se llame tu modelo

# ... dentro de tu clase ...
    @action(detail=True, methods=['post'])
    def descontar(self, request, pk=None):
        # Ruff decía que 'insumo' no se usaba, así que o lo usas o lo quitas
        # Si quieres validar el objeto antes de actualizar:
        insumo = self.get_object() 
        
        cantidad = int(request.data.get('cantidad', 0))
        
        # El error 'F' undefined se quita con la importación de arriba
        Insumo.objects.filter(pk=pk).update(stock_actual=F('stock_actual') - cantidad)
        
        return Response({'status': 'Stock actualizado con éxito'})