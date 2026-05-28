"""
Pruebas de contrato de autenticación para Backend 1.

El registro, login, logout y refresh pertenecen al Módulo 5 (Seguridad).
Backend 1 solo valida JWT, construye request.user en memoria y aplica
permisos usando el claim role. No sincroniza usuarios locales.
"""
from uuid import uuid4

from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.common.authentication import StatelessPetCareUser
from apps.common.roles import OWNER, RECEPTIONIST, VET


def module5_access_token(*, user_id=None, email="usuario@test.com", role=OWNER, **claims):
    token = AccessToken()
    token[settings.SIMPLE_JWT["USER_ID_CLAIM"]] = str(user_id or uuid4())
    token["email"] = email
    token["role"] = role
    for key, value in claims.items():
        token[key] = value
    return str(token)


class Module5JWTContractTests(APITestCase):
    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_backend1_accepts_valid_module5_jwt_on_local_me(self):
        user_id = uuid4()
        self.authenticate(module5_access_token(user_id=user_id, email="owner@test.com", role=OWNER))

        res = self.client.get("/api/v1/auth/me/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], str(user_id))
        self.assertEqual(res.data["email"], "owner@test.com")
        self.assertEqual(res.data["role"], OWNER)
        self.assertTrue(res.data["is_active"])

    def test_backend1_rejects_invalid_bearer_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token-invalido-del-modulo-5")

        res = self.client.get("/api/v1/auth/me/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_claim_from_module5_jwt_drives_permissions(self):
        self.authenticate(module5_access_token(role=OWNER))
        owner_res = self.client.get("/api/v1/owners/")
        self.assertEqual(owner_res.status_code, status.HTTP_403_FORBIDDEN)

        self.authenticate(module5_access_token(role=RECEPTIONIST))
        receptionist_res = self.client.get("/api/v1/owners/")
        self.assertNotEqual(receptionist_res.status_code, status.HTTP_403_FORBIDDEN)

    def test_token_without_user_id_is_rejected(self):
        token = AccessToken()
        token["email"] = "owner@test.com"
        token["role"] = OWNER
        self.authenticate(str(token))

        res = self.client.get("/api/v1/auth/me/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_without_email_is_rejected(self):
        token = AccessToken()
        token["user_id"] = str(uuid4())
        token["role"] = OWNER
        self.authenticate(str(token))

        res = self.client.get("/api/v1/auth/me/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_without_role_is_rejected(self):
        token = AccessToken()
        token["user_id"] = str(uuid4())
        token["email"] = "owner@test.com"
        self.authenticate(str(token))

        res = self.client.get("/api/v1/auth/me/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_with_invalid_role_is_rejected(self):
        self.authenticate(module5_access_token(role="ADMIN"))

        res = self.client.get("/api/v1/auth/me/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_with_inactive_claim_is_rejected_when_claim_exists(self):
        self.authenticate(module5_access_token(role=OWNER, is_active=False))

        res = self.client.get("/api/v1/auth/me/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_returns_stateless_user(self):
        user_id = uuid4()
        user = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"][0]
        self.assertEqual(user, "apps.common.authentication.PetCareJWTAuthentication")
        self.assertEqual(StatelessPetCareUser(id=str(user_id), email="vet@test.com", role=VET).role_name, VET)
