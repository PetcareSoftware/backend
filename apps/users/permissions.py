from rest_framework.permissions import BasePermission

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