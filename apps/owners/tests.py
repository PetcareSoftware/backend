from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class OwnerEndpointsTests(APITestCase):
    """
    Pruebas unitarias para verificar el funcionamiento de los endpoints de propietarios.
    """

    def test_owner_me_get(self):
        # Verifica la obtención de la información del perfil del propietario autenticado.
        url = reverse('owner-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_owner_me_patch(self):
        # Verifica la actualización de datos (PATCH) del perfil del propietario autenticado.
        url = reverse('owner-me')
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_owner_me_pets(self):
        # Verifica el registro de una nueva mascota vinculada directamente al propietario.
        url = reverse('owner-me-pets')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
