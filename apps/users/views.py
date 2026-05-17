from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .permissions import esGerente
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class PanelGerenteView(APIVIew):
    #Aqui damos doble seguridad, tiene que estar logueado y tiene que ser gerente 
    Permission_classes = [IsAuthenticated,esGerente]

    def get(self,request):
        datos_sensibles = {
            "mensaje": "Bienvenido gerente. Tienes acceso a esta informacion confidencial.",
            "usuario_actual": request.user.email,
            "rol": request.user.rol 
        }
        return Response(datos_sensibles, status=status.HTTP_200_OK)
    
class VerificarUsuarioView(APIView):
    #autoricacion
    Permission_classes = [IsAuthenticated]

    def get(self,request):
        #Este es el undepoint que devuelve los datos a los usuarios dueño del token
        user =  request.user
        return  Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "rol": getattr(user, 'rol', 'sin_rol')
        })