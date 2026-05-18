from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth import authenticate, login
from django.db.models import F
from .models import Insumo
from .serializers import InsumoSerializer

@api_view(['POST'])
def login_veterinario(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        es_veterinario = user.groups.filter(name='Veterinario').exists()

        if es_veterinario:
            login(request, user)
            return Response(
                {"mensaje": "Bienvenido doctor, autorización exitosa"}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Acceso denegado. Esta ruta es exclusiva para personal veterinario"}, 
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        return Response(
            {"error": "Usuario o lacontraseña son incorrectos"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

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