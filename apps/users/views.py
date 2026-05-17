from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsRecepcionista

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