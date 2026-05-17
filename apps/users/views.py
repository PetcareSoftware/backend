from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login

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