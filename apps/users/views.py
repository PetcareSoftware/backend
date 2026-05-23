from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .permissions import IsRecepcionista
from .permissions import IsRecepcionista, esGerente
from .models import LogEntry
from .serializers import LogEntrySerializer

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
    pagination_class = LogEntryPagination
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, esGerente]

    def get(self, request):
        queryset = LogEntry.objects.select_related('user').all()

        # Filtro por ID de usuario
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filtro por fecha/hora desde
        desde = request.query_params.get('desde')
        if desde:
            desde_dt = parse_datetime(desde)
            if desde_dt:
                queryset = queryset.filter(timestamp__gte=desde_dt)

        # Filtro por fecha/hora hasta
        hasta = request.query_params.get('hasta')
        if hasta:
            hasta_dt = parse_datetime(hasta)
            if hasta_dt:
                queryset = queryset.filter(timestamp__lte=hasta_dt)

        # Filtro por tipo de acción
        action = request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)

        # Paginación
        paginator = LogEntryPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = LogEntrySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    
@method_decorator(login_required, name='dispatch')
class PanelLogsView(TemplateView):
    template_name = 'panel_logs.html'

    def dispatch(self, request, *args, **kwargs):
        # Comprobación adicional: debe ser Gerente
        if not request.user.groups.filter(name='Gerente').exists():
            return HttpResponseForbidden("Acceso denegado: solo el Gerente puede ver esta página.")
        return super().dispatch(request, *args, **kwargs)