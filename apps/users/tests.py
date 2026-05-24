from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class UserAuthEndpointsTests(APITestCase):
    """
    Pruebas unitarias para verificar el funcionamiento de los endpoints de autenticación de usuarios.
    """

    def test_auth_register(self):
        # Verifica el endpoint de registro de un nuevo propietario en el sistema.
        url = reverse('auth-register')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_auth_login(self):
        # Verifica el endpoint de inicio de sesión para obtener el token de acceso.
        url = reverse('auth-login')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_auth_refresh(self):
        # Verifica el endpoint para refrescar el token de acceso una vez expirado.
        url = reverse('auth-refresh')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
