from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def notifications_list(request):
    """
    GET /api/v1/notifications/
    Obtener la lista de notificaciones recientes dirigidas al usuario autenticado.
    """
    return Response({})

@api_view(['PATCH'])
def notification_read(request, notification_id):
    """
    PATCH /api/v1/notifications/{notification_id}/read/
    Marcar una única notificación como "leída".
    """
    return Response({})

@api_view(['PATCH'])
def notification_read_all(request):
    """
    PATCH /api/v1/notifications/read-all/
    Acción en masa para marcar todas las notificaciones pendientes como "leídas" a la vez.
    """
    return Response({})
