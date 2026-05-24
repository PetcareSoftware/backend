from django.contrib.auth import authenticate, login
from django.db.models import F
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden

from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import RegistroAuditoriaSerializer
from .models import RegistroAuditoria
from .models import Insumo
from .serializers import InsumoSerializer
from .permissions import IsRecepcionista, esGerente

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
            {"error": "Usuario o la contraseña son incorrectos"}, 
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

class RecepcionistaTestView(APIView):
    """
    Vista de prueba protegida: solo accesible para usuarios con permisos de recepcionista.
    """
    permission_classes = [IsAuthenticated, IsRecepcionista]

    def get(self, request):
        return Response({
            "mensaje": "Acceso concedido: Eres recepcionista.",
            "usuario": request.user.username
        })

class PanelGerenteView(APIView):
    # Aquí damos doble seguridad, tiene que estar logueado y tiene que ser gerente 
    permission_classes = [IsAuthenticated, esGerente]

    def get(self, request):
        datos_sensibles = {
            "mensaje": "Bienvenido gerente. Tienes acceso a esta informacion confidencial.",
            "usuario_actual": request.user.email,
            "rol": getattr(request.user, 'rol', 'sin_rol') 
        }
        return Response(datos_sensibles, status=status.HTTP_200_OK)
    
class VerificarUsuarioView(APIView):
    # Autorización
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Este es el endpoint que devuelve los datos al usuario dueño del token
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "rol": getattr(user, 'rol', 'sin_rol')
        })
        
        
class LogEntryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class LogEntryListView(APIView):
    """
    Endpoint protegido que permite al Gerente consultar los registros de auditoría.
    Soporta filtros por usuario, rango de fechas y tipo de acción.
    """
    permission_classes = [IsAuthenticated, esGerente]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request):
        queryset = RegistroAuditoria.objects.select_related('usuario').all()

        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(usuario_id=user_id)

        desde = request.query_params.get('desde')
        if desde:
            desde_dt = parse_datetime(desde)
            if desde_dt:
                queryset = queryset.filter(fecha__gte=desde_dt)

        hasta = request.query_params.get('hasta')
        if hasta:
            hasta_dt = parse_datetime(hasta)
            if hasta_dt:
                queryset = queryset.filter(fecha__lte=hasta_dt)

        action = request.query_params.get('action')
        if action:
            queryset = queryset.filter(accion=action)

        paginator = LogEntryPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = RegistroAuditoriaSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

@method_decorator(login_required, name='dispatch')
class PanelLogsView(TemplateView):
    template_name = 'panel_logs.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Gerente').exists():
            return HttpResponseForbidden("Acceso denegado: solo el Gerente puede ver esta página.")
        return super().dispatch(request, *args, **kwargs)