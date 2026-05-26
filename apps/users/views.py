from django.contrib.auth import authenticate, login
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Supply, AuditLog
from .serializers import SupplySerializer, AuditLogSerializer

# Importamos las nuevas clases de permisos de seguridad
from .permissions import (
    DjangoModelPermissions,
    CustomModelPermissions,
    IsReceptionist,
    IsOwner
)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_veterinarian(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        is_veterinarian = user.groups.filter(name='veterinarian').exists()
        if is_veterinarian:
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

class SupplyViewSet(viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer
    permission_classes = [DjangoModelPermissions]
    
    @action(detail=True, methods=['post'])
    def deduct(self, request, pk=None):
        supply = self.get_object()
        try:
            quantity_str = request.data.get('quantity', 0)
            quantity = int(quantity_str)
            if quantity <= 0:
                return Response({'error': 'La cantidad debe ser mayor a cero'}, status=status.HTTP_400_BAD_REQUEST)
                
            Supply.objects.filter(pk=pk).update(current_stock=F('current_stock') - quantity)
            return Response({'status': 'Stock actualizado con éxito'}, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response({'error': 'Cantidad no válida'}, status=status.HTTP_400_BAD_REQUEST)

class ReceptionistTestView(APIView):
    permission_classes = [IsAuthenticated, IsReceptionist]
    def get(self, request):
        return Response({"mensaje": "Acceso concedido: Eres recepcionista.", "usuario": request.user.username})

class ManagerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    def get(self, request):
        sensitive_data = {
            "mensaje": "Bienvenido gerente. Tienes acceso a esta informacion confidencial.",
            "usuario_actual": request.user.email,
            "rol": getattr(request.user, 'role', 'sin_rol')
        }
        return Response(sensitive_data, status=status.HTTP_200_OK)
    
class VerifyUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "rol": getattr(user, 'role', 'sin_rol')
        })

# --- CLASE AÑADIDA PARA RESOLVER EL ERROR ---
class LogDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOwner] # Solo el dueño/gerente debería ver logs

    def get(self, request):
        logs = AuditLog.objects.all().order_by('-timestamp')[:50]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)