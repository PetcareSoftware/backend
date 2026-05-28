from datetime import date, time

from django.utils import timezone
from rest_framework import status

from apps.appointments.models import Appointment
from apps.schedules.models import TimeSlot
from tests.base import PetCareAPITestCase


class AppointmentTests(PetCareAPITestCase):
    def create_today_appointment(self, pet=None, start_time=time(9, 0)):
        slot = TimeSlot.objects.create(
            vet=self.vet,
            date=date.today(),
            start_time=start_time,
            end_time=time(start_time.hour, min(start_time.minute + 30, 59)),
            status=TimeSlot.Status.BOOKED,
        )
        return Appointment.objects.create(
            pet=pet or self.pet,
            vet=self.vet,
            slot=slot,
            reason='Consulta de hoy',
            status=Appointment.Status.SCHEDULED,
            scheduled_at=timezone.now(),
        )

    def test_create_blocks_slot_and_receptionist_can_book_any_pet(self):
        res = self.create_appointment()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.status, TimeSlot.Status.BOOKED)
        other_slot = TimeSlot.objects.filter(
            vet=self.vet,
            date=self.tomorrow,
            status=TimeSlot.Status.FREE,
        ).first()
        self.auth(self.receptionist)
        res = self.client.post(
            '/api/v1/appointments/',
            {
                'pet_id': str(self.other_pet.id),
                'vet_id': str(self.vet.user_id),
                'slot_id': str(other_slot.id),
                'reason': 'Recepcion',
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_owner_cannot_book_other_pet_and_deleted_pet_400(self):
        self.auth(self.owner_user)
        res = self.client.post(
            '/api/v1/appointments/',
            {
                'pet_id': str(self.other_pet.id),
                'vet_id': str(self.vet.user_id),
                'slot_id': str(self.slot.id),
                'reason': 'Hack',
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.pet.is_deleted = True
        self.pet.save(update_fields=['is_deleted'])
        res = self.client.post(
            '/api/v1/appointments/',
            {
                'pet_id': str(self.pet.id),
                'vet_id': str(self.vet.user_id),
                'slot_id': str(self.slot.id),
                'reason': 'x',
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_slot_conflict(self):
        first = self.create_appointment()
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.create_appointment()
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)

    def test_patch_reschedule_slot_id_maps_to_new_slot_id(self):
        res = self.create_appointment()
        appointment_id = res.data['id']
        new_slot = TimeSlot.objects.filter(
            vet=self.vet,
            date=self.tomorrow,
            status=TimeSlot.Status.FREE,
        ).exclude(id=self.slot.id).first()
        self.auth(self.owner_user)
        res = self.client.patch(
            f'/api/v1/appointments/{appointment_id}/',
            {'slot_id': str(new_slot.id)},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.slot.refresh_from_db()
        new_slot.refresh_from_db()
        self.assertEqual(self.slot.status, TimeSlot.Status.FREE)
        self.assertEqual(new_slot.status, TimeSlot.Status.BOOKED)

    def test_cancel_releases_and_reuses_slot_and_foreign_owner_403(self):
        res = self.create_appointment()
        appointment_id = res.data['id']
        self.auth(self.other_owner_user)
        foreign = self.client.post(f'/api/v1/appointments/{appointment_id}/cancel/', {}, format='json')
        self.assertEqual(foreign.status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.owner_user)
        res = self.client.post(
            f'/api/v1/appointments/{appointment_id}/cancel/',
            {'cancellation_reason': 'No puedo'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.status, TimeSlot.Status.FREE)
        res = self.create_appointment()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_cancel_completed_and_cancelled_422(self):
        res = self.create_appointment()
        appointment_id = res.data['id']
        appt = Appointment.objects.get(id=appointment_id)
        appt.status = Appointment.Status.COMPLETED
        appt.save(update_fields=['status'])
        self.auth(self.owner_user)
        response = self.client.post(f'/api/v1/appointments/{appointment_id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        appt.status = Appointment.Status.CANCELLED
        appt.save(update_fields=['status'])
        response = self.client.post(f'/api/v1/appointments/{appointment_id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_check_in_codes_today_only_and_waiting_order(self):
        future = self.create_appointment()
        future_id = future.data['id']
        self.auth(self.receptionist)
        response = self.client.post(f'/api/v1/appointments/{future_id}/check-in/')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        appointment = self.create_today_appointment()
        self.auth(self.owner_user)
        response = self.client.post(f'/api/v1/appointments/{appointment.id}/check-in/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.receptionist)
        res = self.client.post(f'/api/v1/appointments/{appointment.id}/check-in/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['appointment_id'], str(appointment.id))
        self.assertEqual(res.data['status'], Appointment.Status.CHECKED_IN)
        self.assertEqual(res.data['waiting_entry']['position'], 1)
        self.assertIsNone(res.data['waiting_entry']['called_at'])
        response = self.client.post(f'/api/v1/appointments/{appointment.id}/check-in/')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        listing = self.client.get('/api/v1/waiting-list/')
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertIn('date', listing.data)
        self.assertEqual(listing.data['entries'][0]['id'], res.data['waiting_entry']['id'])

    def test_call_next_only_next_patient(self):
        first_appt = self.create_today_appointment(self.pet, time(9, 0))
        second_appt = self.create_today_appointment(self.other_pet, time(10, 0))
        self.auth(self.receptionist)
        first = self.client.post(f'/api/v1/appointments/{first_appt.id}/check-in/').data['waiting_entry']
        second = self.client.post(f'/api/v1/appointments/{second_appt.id}/check-in/').data['waiting_entry']
        wrong = self.client.post(f"/api/v1/waiting-list/{second['id']}/call-next/")
        self.assertEqual(wrong.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        ok = self.client.post(f"/api/v1/waiting-list/{first['id']}/call-next/")
        self.assertEqual(ok.status_code, status.HTTP_200_OK)

    def test_today_dashboard_restricted_and_invalid_vet_404(self):
        self.auth(self.owner_user)
        self.assertEqual(self.client.get('/api/v1/appointments/today/').status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.receptionist)
        self.assertEqual(self.client.get('/api/v1/appointments/today/').status_code, status.HTTP_200_OK)
        self.auth(self.vet_user)
        vet_today = self.client.get('/api/v1/appointments/today/')
        self.assertEqual(vet_today.status_code, status.HTTP_200_OK)
        by_vet = self.client.get(f'/api/v1/appointments/today/by-vet/{self.vet.user_id}/')
        self.assertEqual(by_vet.status_code, status.HTTP_200_OK)
        self.assertEqual(by_vet.data['vet']['id'], str(self.vet.user_id))
        self.assertIn('date', by_vet.data)
        self.assertIn('appointments', by_vet.data)
        self.auth(self.receptionist)
        missing = self.client.get('/api/v1/appointments/today/by-vet/00000000-0000-0000-0000-000000000000/')
        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)

    def test_vet_waiting_list_permissions(self):
        appointment = self.create_today_appointment()
        self.auth(self.receptionist)
        check_in = self.client.post(f'/api/v1/appointments/{appointment.id}/check-in/')
        self.assertEqual(check_in.status_code, status.HTTP_200_OK)

        self.auth(self.vet_user)
        own = self.client.get(f'/api/v1/vets/{self.vet.user_id}/waiting-list/')
        self.assertEqual(own.status_code, status.HTTP_200_OK)
        self.assertIn('entries', own.data)

        other = self.client.get(f'/api/v1/vets/{self.other_vet.user_id}/waiting-list/')
        self.assertEqual(other.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.receptionist)
        recep = self.client.get(f'/api/v1/vets/{self.vet.user_id}/waiting-list/')
        self.assertEqual(recep.status_code, status.HTTP_200_OK)

        self.auth(self.owner_user)
        owner = self.client.get(f'/api/v1/vets/{self.vet.user_id}/waiting-list/')
        self.assertEqual(owner.status_code, status.HTTP_403_FORBIDDEN)
