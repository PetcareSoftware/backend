from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class PatientEndpointsTests(APITestCase):
    """
    Pruebas unitarias para verificar el funcionamiento de los endpoints de pacientes (mascotas).
    """

    def test_pet_medical_record_summary(self):
        # Verifica la obtención del resumen rápido del expediente de salud de una mascota (alergias, última consulta, etc.).
        url = reverse('pet-medical-record-summary', kwargs={'pet_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_pet_medical_record(self):
        # Verifica la consulta del historial clínico completo con todas las visitas pasadas de la mascota.
        url = reverse('pet-medical-record', kwargs={'pet_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_pet_vaccination_schedule(self):
        # Verifica el cronograma/planificador de vacunas programadas y aplicadas de la mascota.
        url = reverse('pet-vaccination-schedule', kwargs={'pet_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_pet_vaccination_events(self):
        # Verifica el registro de un evento de aplicación de vacuna para la mascota.
        url = reverse('pet-vaccination-events', kwargs={'pet_id': 1})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
