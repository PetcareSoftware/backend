from django.contrib.auth import authenticate, login
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import AuditLog
from .serializers import AuditLogSerializer

# Importamos las nuevas clases de permisos de seguridad
from .permissions import (
    DjangoModelPermissions,
    CustomModelPermissions,
    IsReceptionist,
    IsOwner,
    IsManager
)
class ReceptionistTestView(APIView):
    permission_classes = [IsReceptionist]
    def get(self, request):
        return Response({"mensaje": "Acceso concedido: Eres recepcionista.", "usuario": request.user.username})

class ManagerDashboardView(APIView):
    permission_classes = [IsOwner]
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


class LogDashboardView(APIView):
    permission_classes = [IsAdminUser | IsManager]

    def get(self, request):
        logs = AuditLog.objects.all().order_by('-timestamp')[:50]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    class AdminStaffLoginView(APIView):
        permission_classes = [AllowAny] # El intento de login debe ser público para recibir los datos

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            is_gerente = user.groups.filter(name='manager').exists()
            
            # Verificamos si cumple con los roles requeridos
            if user.is_staff or is_gerente:
                login(request, user) # Creamos la sesión exclusivamente para el panel de auditoría
                return Response({"mensaje": "Bienvenido, acceso de administración autorizado."}, status=status.HTTP_200_OK)
            
            return Response({"error": "Acceso denegado. Solo Gerentes o Staff."}, status=status.HTTP_403_FORBIDDEN)
            
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)