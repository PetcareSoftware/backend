from rest_framework import permissions


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
