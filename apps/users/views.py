from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .permissions import esGerente


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