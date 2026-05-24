from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class NotificationEndpointsTests(APITestCase):
    """
    Pruebas unitarias para verificar el funcionamiento de los endpoints de notificaciones.
    """

    def test_notifications_list(self):
        # Verifica el listado de las notificaciones del usuario actual.
        url = reverse('notifications-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_notification_read(self):
        # Verifica marcar una notificación específica como leída.
        url = reverse('notification-read', kwargs={'notification_id': 7})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_notification_read_all(self):
        # Verifica marcar todas las notificaciones pendientes como leídas en lote.
        url = reverse('notification-read-all')
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
