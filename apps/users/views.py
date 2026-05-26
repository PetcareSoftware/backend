from django.contrib.auth import authenticate, login
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Insumo
from .serializers import InsumoSerializer

# Importamos las nuevas clases de permisos de seguridad
from .permissions import (
    DjangoModelPermissions,
    CustomModelPermissions,
    IsReceptionist,
    IsOwner
)

@api_view(['POST'])
@permission_classes([AllowAny]) # El login debe ser público para poder entrar
def login_veterinario(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        # Validación de pertenencia al rol mediante Grupos
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
            {"error": "Usuario o la contraseña son incorrectos"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    
    # AQUÍ ESTÁ EL REQUERIMIENTO PRINCIPAL: Permiso estándar de modelo
    permission_classes = [DjangoModelPermissions]
    
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

class RecepcionistaTestView(APIView):
    """
    Vista de prueba protegida: solo accesible para usuarios con permisos de recepcionista.
    """
    # Utiliza la validación por roles
    permission_classes = [IsAuthenticated, IsReceptionist]

    def get(self, request):
        return Response({
            "mensaje": "Acceso concedido: Eres recepcionista.",
            "usuario": request.user.username
        })

class PanelGerenteView(APIView):
    # Utiliza la validación por roles
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        datos_sensibles = {
            "mensaje": "Bienvenido gerente. Tienes acceso a esta informacion confidencial.",
            "usuario_actual": request.user.email,
            "rol": getattr(request.user, 'rol', 'sin_rol') 
        }
        return Response(datos_sensibles, status=status.HTTP_200_OK)
    
class VerificarUsuarioView(APIView):
    # Autorización general
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filtro natural: el usuario solo puede ver y devolver sus propios datos
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "rol": getattr(user, 'rol', 'sin_rol')
        })