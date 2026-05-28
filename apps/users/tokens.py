from rest_framework_simplejwt.tokens import RefreshToken


class PetCareRefreshToken(RefreshToken):
    """Refresh token local compatible con el payload mínimo de Módulo 5."""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["email"] = user.email
        token["role"] = user.role_name
        token["is_active"] = bool(user.is_active)
        return token


def build_token_pair(user):
    refresh = PetCareRefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}
