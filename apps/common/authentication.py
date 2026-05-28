from dataclasses import dataclass
from uuid import UUID

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.settings import api_settings

from apps.common.roles import ROLE_CHOICES


VALID_ROLE_CODES = {code for code, _label in ROLE_CHOICES}


def _claim_is_true(value):
    """Normaliza el claim opcional is_active emitido por Seguridad/Módulo 5."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


@dataclass(frozen=True)
class StatelessPetCareUser:
    """
    Usuario en memoria construido desde el JWT del Módulo 5.

    Backend 1 no crea ni sincroniza usuarios locales mientras Base de Datos no
    entregue los modelos definitivos. Este objeto cumple el contrato mínimo que
    DRF necesita para request.user y permisos por rol.
    """

    id: str
    email: str
    role: str
    is_active: bool = True

    @property
    def pk(self):
        return self.id

    @property
    def role_name(self):
        return self.role

    @property
    def username(self):
        return self.email

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_staff(self):
        return self.role in {"MANAGER", "RECEPTIONIST"}

    @property
    def is_superuser(self):
        return False

    def get_username(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return False

    def has_module_perms(self, app_label):
        return False


class PetCareJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT stateless compatible con el Módulo 5 (Seguridad).

    Payload mínimo esperado:
      {
        "user_id": "uuid-v4",
        "email": "usuario@ejemplo.com",
        "role": "OWNER|RECEPTIONIST|VET|TECH_VET|MANAGER"
      }

    El claim "is_active" es opcional por compatibilidad. Si Seguridad lo envía
    con valor falso, Backend 1 rechaza el token. No se consulta ni modifica la
    base de datos durante la autenticación.
    """

    def get_user(self, validated_token):
        user_id = self._required_claim(validated_token, api_settings.USER_ID_CLAIM)
        email = self._required_claim(validated_token, "email")
        role = self._required_claim(validated_token, "role")

        try:
            UUID(str(user_id), version=4)
        except (TypeError, ValueError) as exc:
            raise InvalidToken("El token contiene un user_id inválido.") from exc

        if not isinstance(email, str) or "@" not in email:
            raise AuthenticationFailed(
                "El token contiene un email inválido.",
                code="invalid_email_claim",
            )

        if role not in VALID_ROLE_CODES:
            raise AuthenticationFailed(
                "El token contiene un rol no soportado por Backend 1.",
                code="invalid_role_claim",
            )

        if "is_active" in validated_token and not _claim_is_true(validated_token.get("is_active")):
            raise AuthenticationFailed(
                "Usuario inactivo según el Módulo 5 de Seguridad.",
                code="user_inactive",
            )

        return StatelessPetCareUser(
            id=str(user_id),
            email=email.strip().lower(),
            role=role,
            is_active=True,
        )

    @staticmethod
    def _required_claim(validated_token, claim):
        value = validated_token.get(claim)
        if value in (None, ""):
            raise InvalidToken(f"El token no contiene {claim}.")
        return value
