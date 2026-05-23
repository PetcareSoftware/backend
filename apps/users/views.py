from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def register(request):
    """
    POST /api/v1/auth/register/
    Registrar a un nuevo propietario de mascota en el sistema.
    """
    return Response({'message': 'auth register stub'})

@api_view(['POST'])
def login(request):
    """
    POST /api/v1/auth/login/
    Autenticar a cualquier usuario (veterinario, administrador, o propietario) y devolver un token de acceso.
    """
    return Response({'message': 'auth login stub'})

@api_view(['POST'])
def refresh(request):
    """
    POST /api/v1/auth/refresh/
    Renovar el token de acceso cuando el anterior haya expirado.
    """
    return Response({'message': 'auth refresh stub'})
