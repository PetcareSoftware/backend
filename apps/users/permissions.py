<<<<<<< HEAD
<<<<<<< HEAD

from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsTecnicoVeterinario(permissions.BasePermission):
    """
    Permite acceso solo si el usuario es Admin o pertenece al grupo Tecnico_Veterinario.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # El superusuario (admin) tiene permiso total
        if request.user.is_superuser:
            return True

        # Verifica si el usuario está en el grupo correcto
        return request.user.groups.filter(name="Tecnico_Veterinario").exists()


# Lista de codenames que definen al recepcionista
RECEPCIONISTA_PERMISSIONS = [
    'auth.add_manual_appointment',
    'auth.view_calendar_availability',
    'auth.register_attendance',
    'auth.manage_waitlist',
    'auth.view_appointment_history',
]

class IsRecepcionista(BasePermission):
    """
    Permiso personalizado que concede acceso si el usuario autenticado
    posee al menos uno de los permisos del rol de recepcionista.
    """
    def has_permission(self, request, view):
        # Si el usuario no está autenticado, deniega automáticamente
        if not request.user or not request.user.is_authenticated:
            return False

        # Obtiene todos los codenames de permisos del usuario
        user_permissions = request.user.get_all_permissions()

        # Verifica si alguno de los permisos del recepcionista está presente
        return any(perm in user_permissions for perm in RECEPCIONISTA_PERMISSIONS)

=======
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
>>>>>>> 114d067091390597f672b398e86b349a4422f02b
=======
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
    
    
>>>>>>> 9c51a2513fcf2786e671f118305d1f648925711f
