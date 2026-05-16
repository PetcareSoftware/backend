from rest_framework import permissions

class EsCliente(permissions.BasePermission):
    """
    Este es tu 'guardia de seguridad'. 
    Solo dejará pasar la petición si el usuario es un Cliente.
    """
    
    def has_permission(self, request, view):
        # 1. Primero verifica que el usuario haya iniciado sesión (que no sea anónimo)
        if not request.user or not request.user.is_authenticated:
            return False
            
        # 2. Luego verifica si pertenece al grupo de 'Cliente'
        # (Asumiendo que los roles se manejan por grupos)
        return request.user.groups.filter(name='Cliente').exists()