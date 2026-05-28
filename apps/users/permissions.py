from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import groups

# --- Listas de permisos basadas en el documento de roles ---

RECEPTIONIST_PERMISSIONS = [
    'auth.add_manual_appointment',
    'auth.view_calendar_availability',
    'auth.register_attendance',
    'auth.manage_waitlist',
    'auth.view_appointment_history',
]

VETERINARIAN_PERMISSIONS = [
    'auth.view_daily_agenda',
    'auth.view_clinical_records',
    'auth.document_medical_record',
    'auth.prescribe_treatment',
    'auth.mark_appointment_completed',
    'auth.deduct_supply_usage',
]

VET_TECHNICIAN_PERMISSIONS = [
    'auth.manage_catalog_crud',
    'auth.manage_stock_levels',
    'auth.process_supply_rest',
    'auth.monitor_stock_alerts',
    'auth.create_purchase_request',
]

MANAGER_PERMISSIONS = [
    'auth.authorize_managerial_requests',
    'auth.manage_purchase_lifecycle',
    'auth.view_business_intelligence_kpis',
    'auth.export_reports',
]

# --- Clases de Permisos ---

class IsVeterinaryTechnician(BasePermission):
    """Permite acceso si el usuario pertenece al grupo 'veterinary_technician'."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name="veterinary_technician").exists()

class HasVeterinarianPermissions(BasePermission):
    """Acceso si el usuario posee los permisos de Veterinario."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_permissions = request.user.get_all_permissions()
        return any(perm in user_permissions for perm in VETERINARIAN_PERMISSIONS)

class HasVetTechnicianPermissions(BasePermission):
    """Acceso si el usuario posee los permisos de Técnico Veterinario."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_permissions = request.user.get_all_permissions()
        return any(perm in user_permissions for perm in VET_TECHNICIAN_PERMISSIONS)

class HasManagerPermissions(BasePermission):
    """Acceso si el usuario posee los permisos de Gerente."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_permissions = request.user.get_all_permissions()
        return any(perm in user_permissions for perm in MANAGER_PERMISSIONS)

class HasReceptionistPermissions(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_permissions = request.user.get_all_permissions()
        return any(perm in user_permissions for perm in RECEPTIONIST_PERMISSIONS)

class IsClient(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='client').exists()

class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='manager').exists()

class CustomModelPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perms(getattr(view, "permission_required", []))

class DjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = permissions.DjangoModelPermissions.perms_map | {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.contains(groups.owner)

class IsReceptionist(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.contains(groups.receptionist)