from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'PATCH'])
def owner_me(request):
    """
    GET /api/v1/owners/me/ -> Obtener la información del perfil del propietario.
    PATCH /api/v1/owners/me/ -> Actualizar datos del perfil del propietario autenticado.
    """
    if request.method == 'GET':
        return Response({'message': 'get owner profile stub'})
    elif request.method == 'PATCH':
        return Response({'message': 'update owner profile stub'})

@api_view(['POST'])
def owner_me_pets(request):
    """
    POST /api/v1/owners/me/pets/
    Registrar una nueva mascota asociada directamente al perfil del propietario autenticado.
    """
    return Response({'message': 'register new pet stub'})
