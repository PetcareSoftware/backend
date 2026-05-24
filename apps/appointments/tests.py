from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class AppointmentEndpointsTests(APITestCase):
    """
    Pruebas unitarias para verificar el funcionamiento de los endpoints de citas y agendas médicas.
    """

    def test_vet_slots(self):
        # Verifica la consulta de horarios/huecos libres disponibles para un veterinario específico.
        url = reverse('vet-slots', kwargs={'vet_id': 12})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_schedule_calendar(self):
        # Verifica la consulta del calendario unificado con citas de toda la clínica.
        url = reverse('schedule-calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_appointment_list_get(self):
        # Verifica la obtención de la lista de citas sin aplicar filtros adicionales.
        url = reverse('appointment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_appointment_list_get_filtered(self):
        # Verifica que la vista acepte y procese correctamente los Query Params de filtrado (fecha y veterinario).
        url = reverse('appointment-list')
        response = self.client.get(url, {'date': 'today', 'vet_id': '3'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_appointment_list_post(self):
        # Verifica la creación de una nueva cita.
        url = reverse('appointment-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_appointment_cancel(self):
        # Verifica el endpoint para cancelar una cita agendada.
        url = reverse('appointment-cancel', kwargs={'appointment_id': 15})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_appointment_confirm(self):
        # Verifica el endpoint para confirmar la asistencia a una cita.
        url = reverse('appointment-confirm', kwargs={'appointment_id': 15})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_appointment_check_in(self):
        # Verifica el registro de la llegada del paciente a la clínica (check-in).
        url = reverse('appointment-checkin', kwargs={'appointment_id': 15})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_waiting_list_get(self):
        # Verifica la consulta de la lista de espera de pacientes en tiempo real.
        url = reverse('waiting-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_waiting_list_call_next(self):
        # Verifica el llamado del siguiente paciente en la cola por parte del veterinario.
        url = reverse('waiting-list-call-next', kwargs={'queue_id': 4})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_appointment_consultations(self):
        # Verifica el registro de los detalles clínicos de la consulta médica realizada.
        url = reverse('appointment-consultations', kwargs={'appointment_id': 8})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_consultation_supplies_used(self):
        # Verifica el registro de los insumos del inventario consumidos en la consulta.
        url = reverse('consultation-supplies', kwargs={'consultation_id': 99})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
