from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import groups

class IsVeterinaryTechnician(BasePermission):
    """
    Permite acceso solo si el usuario es Admin o pertenece al grupo 'veterinary_technician'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Verifica si el usuario está en el grupo correcto
        return request.user.groups.filter(name="veterinary_technician").exists()
    


# Lista de codenames que definen al recepcionista
RECEPTIONIST_PERMISSIONS = [
    'auth.add_manual_appointment',
    'auth.view_calendar_availability',
    'auth.register_attendance',
    'auth.manage_waitlist',
    'auth.view_appointment_history',
]

class HasReceptionistPermissions(BasePermission):
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
        return any(perm in user_permissions for perm in RECEPTIONIST_PERMISSIONS)


class IsClient(BasePermission):
    """
    Este es tu 'guardia de seguridad'.
    Solo dejará pasar la petición si el usuario es un Cliente.
    """
    def has_permission(self, request, view):
        # 1. Primero verifica que el usuario haya iniciado sesión (que no sea anónimo)
        if not request.user or not request.user.is_authenticated:
            return False
            
        # 2. Luego verifica si pertenece al grupo de 'client'
        return request.user.groups.filter(name='client').exists()


class IsManager(BasePermission):
    """
    Permite acceso solo si el usuario está autenticado y pertenece al grupo 'manager'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='manager').exists()


class CustomModelPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Verifica si el usuario tiene los permisos específicos que la vista requiere
        return request.user.has_perms(getattr(view, "permission_required", []))


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = permissions.DjangoModelPermissions.perms_map | {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }
    

class IsOwner(permissions.BasePermission):
    """
    Guardia de seguridad para los dueños del sistema.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Verifica si el usuario tiene el carnet del grupo 'owner'
        return request.user.groups.contains(groups.owner)


class IsReceptionist(permissions.BasePermission):
    """
    Guardia de seguridad para las recepcionistas.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Verifica si el usuario tiene el carnet del grupo 'receptionist'
        return request.user.groups.contains(groups.receptionist)