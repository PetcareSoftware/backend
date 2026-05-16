from rest_framework import permissions

class esGerente(permissions.BasePermission):
    
    def has_permission(self,request,viwe):
        #verificamos que el usuario si realmente haya iniciado sesion
        if not request.user or not request.useris_authentificated:
            return False
        #verificamos si tiene el rol de gerente 
        if hasattr(request.user,'rol') and request.user.rol== 'gerente':
            return True

        return False
    
    