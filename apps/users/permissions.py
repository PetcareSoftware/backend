"""
Compatibilidad con el módulo de seguridad de PetcareSoftware.

La lógica real vive en apps.common.permissions para no duplicar reglas de rol.
Este módulo conserva los nombres usados por el repositorio de referencia
(`IsRecepcionista`, `EsCliente`, `esGerente`, `IsTecnicoVeterinario`) y los
mapea a los roles canónicos de Backend 1.
"""

from apps.common.permissions import (
    IsClinicalStaff,
    IsManager,
    IsOwner,
    IsReceptionist,
    IsTechVet,
    IsVet,
    IsVetOrReceptionist,
    IsVetReceptionistOrOwner,
)


class IsRecepcionista(IsReceptionist):
    pass


class EsCliente(IsOwner):
    pass


class esGerente(IsManager):  # noqa: N801 - nombre legado del módulo de seguridad
    pass


class IsTecnicoVeterinario(IsTechVet):
    pass


__all__ = [
    "IsClinicalStaff",
    "IsManager",
    "IsOwner",
    "IsReceptionist",
    "IsTechVet",
    "IsVet",
    "IsVetOrReceptionist",
    "IsVetReceptionistOrOwner",
    "IsRecepcionista",
    "EsCliente",
    "esGerente",
    "IsTecnicoVeterinario",
]
