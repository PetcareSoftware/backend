from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Permite el acceso únicamente a usuarios cuyo rol es OWNER.
    Se verifica que el usuario tenga un perfil de Owner asociado y que su role sea 'OWNER'.
    """

    message = 'Solo los propietarios pueden acceder a este recurso.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        if role is None:
            return False
        return role.name == 'OWNER'

    def has_object_permission(self, request, view, obj):
        # Valida que el recurso pertenezca al usuario en sesión
        if hasattr(obj, 'user'):  # Caso de modelo Owner
            return obj.user == request.user
        if hasattr(obj, 'owner'): # Caso de modelo Pet
            return obj.owner.user == request.user
        return False


class IsReceptionist(BasePermission):
    """
    Permite el acceso únicamente a usuarios cuyo rol es RECEPTIONIST.
    """

    message = 'Solo los recepcionistas pueden acceder a este recurso.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        if role is None:
            return False
        return role.name == 'RECEPTIONIST'
