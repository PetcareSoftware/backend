OWNER = 'OWNER'
RECEPTIONIST = 'RECEPTIONIST'
VET = 'VET'
TECH_VET = 'TECH_VET'
MANAGER = 'MANAGER'

ROLE_CHOICES = (
    (OWNER, 'Propietario'),
    (RECEPTIONIST, 'Recepcionista'),
    (VET, 'Veterinario'),
    (TECH_VET, 'Técnico veterinario'),
    (MANAGER, 'Administrador/Gerente'),
)

CLINICAL_ROLES = {VET, TECH_VET, MANAGER}


def role_of(user):
    if not user or not getattr(user, 'is_authenticated', False):
        return None
    role = getattr(user, 'role', None)
    if isinstance(role, str):
        return role
    return getattr(role, 'name', None) or getattr(user, 'role_name', None)


def has_role(user, *roles):
    return role_of(user) in set(roles)
