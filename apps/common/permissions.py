from rest_framework.permissions import BasePermission

from .roles import MANAGER, OWNER, RECEPTIONIST, TECH_VET, VET, has_role, role_of


def request_role(request):
    """
    Devuelve el rol autorizado para el request.

    Prioridad:
    1. request.auth["role"], porque el Módulo 5 es la fuente de identidad.
    2. request.user.role / role_name, solo como fallback de compatibilidad.
    """
    token = getattr(request, "auth", None)
    if token is not None:
        try:
            role = token.get("role")
        except AttributeError:
            role = None
        if role:
            return role
    return role_of(getattr(request, "user", None))


def request_has_role(request, *roles):
    return request_role(request) in set(roles)


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, OWNER)


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, RECEPTIONIST)


class IsVet(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, VET, TECH_VET)


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, MANAGER)


class IsTechVet(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, TECH_VET)


class IsOwnerOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, OWNER, RECEPTIONIST)


class IsVetOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, VET, TECH_VET, RECEPTIONIST)


class IsVetReceptionistOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, VET, TECH_VET, RECEPTIONIST, OWNER)


class IsClinicalStaff(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, VET, TECH_VET, MANAGER)


class IsSelfOwnerOrReceptionist(BasePermission):
    """Objeto Owner: recepción ve cualquiera; owner solo su user_id."""
    def has_permission(self, request, view):
        return request_has_role(request, OWNER, RECEPTIONIST)

    def has_object_permission(self, request, view, obj):
        if request_has_role(request, RECEPTIONIST):
            return True
        obj_user_id = getattr(obj, 'user_id', None) or getattr(getattr(obj, 'user', None), 'id', None)
        request_user_id = getattr(getattr(request, "user", None), "id", None)
        return request_has_role(request, OWNER) and str(obj_user_id) == str(request_user_id)


class IsVetSelfOrManager(BasePermission):
    def has_permission(self, request, view):
        return request_has_role(request, VET, TECH_VET, MANAGER)

    def has_object_permission(self, request, view, obj):
        if request_has_role(request, MANAGER):
            return True
        if not request_has_role(request, VET, TECH_VET):
            return False
        vet_user_id = getattr(obj, 'user_id', None) or getattr(getattr(obj, 'vet', None), 'user_id', None)
        request_user_id = getattr(getattr(request, "user", None), "id", None)
        return str(vet_user_id) == str(request_user_id)


def can_manage_appointment(user, appointment, *, owner=True, receptionist=True, vet=False, manager=False):
    if receptionist and has_role(user, RECEPTIONIST):
        return True
    if manager and has_role(user, MANAGER):
        return True
    if owner and has_role(user, OWNER):
        return str(appointment.pet.owner_id) == str(user.id)
    if vet and has_role(user, VET, TECH_VET):
        return str(appointment.vet_id) == str(user.id)
    return False
