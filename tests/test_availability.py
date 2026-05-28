from datetime import date, timedelta
from rest_framework import status
from tests.base import PetCareAPITestCase
from apps.schedules.models import TimeSlot


class AvailabilityTests(PetCareAPITestCase):
    def test_slots_with_schedule_returns_free_and_not_past(self):
        self.auth(self.owner_user)
        res = self.client.get(f'/api/v1/vets/{self.vet.user_id}/slots/?date={self.tomorrow.isoformat()}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res.data['slots']), 0)
        past = date.today() - timedelta(days=1)
        TimeSlot.objects.create(vet=self.vet, date=past, start_time='08:00', end_time='08:30')
        res = self.client.get(f'/api/v1/vets/{self.vet.user_id}/slots/?date={past.isoformat()}')
        self.assertEqual(res.data['slots'], [])

    def test_invalid_date_and_range_over_30_days_return_400(self):
        self.auth(self.owner_user)
        bad = self.client.get(f'/api/v1/vets/{self.vet.user_id}/slots/?date=bad-date')
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)
        d1 = date.today()
        d2 = d1 + timedelta(days=31)
        res = self.client.get(f'/api/v1/vets/{self.vet.user_id}/availability/?from={d1.isoformat()}&to={d2.isoformat()}')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vet_without_schedule_empty(self):
        self.auth(self.owner_user)
        res = self.client.get(f'/api/v1/vets/{self.other_vet.user_id}/slots/?date={self.tomorrow.isoformat()}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['slots'], [])

    def test_receptionist_cannot_create_schedule_and_vet_can(self):
        self.auth(self.receptionist)
        res = self.client.post(f'/api/v1/vets/{self.vet.user_id}/schedules/', {'day_of_week':1,'start_time':'08:00','end_time':'10:00','slot_duration_min':30}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.vet_user)
        res = self.client.post(f'/api/v1/vets/{self.vet.user_id}/schedules/', {'day_of_week':2,'start_time':'10:00','end_time':'12:00','slot_duration_min':30}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_booked_slot_does_not_appear(self):
        self.slot.status = TimeSlot.Status.BOOKED
        self.slot.save(update_fields=['status'])
        self.auth(self.owner_user)
        res = self.client.get(f'/api/v1/vets/{self.vet.user_id}/slots/?date={self.tomorrow.isoformat()}')
        self.assertFalse(any(str(s['id']) == str(self.slot.id) for s in res.data['slots']))

    def test_calendar_default_today(self):
        self.auth(self.owner_user)
        res = self.client.get('/api/v1/schedules/calendar/')
        self.assertEqual(res.data['from'], date.today().isoformat())
        self.assertEqual(res.data['to'], date.today().isoformat())
