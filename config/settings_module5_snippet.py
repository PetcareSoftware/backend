# Snippet mínimo confirmado por el Módulo 5.
# El proyecto corregido usa un wrapper compatible: apps.common.authentication.PetCareJWTAuthentication
# para poder sincronizar usuarios locales desde claims si Seguridad ya emitió el JWT.

import os


def env(name, default=None):
    return os.environ.get(name, default)


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "SIGNING_KEY": env("JWT_SECRET_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
