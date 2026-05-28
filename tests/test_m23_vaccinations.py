from datetime import date, timedelta
from unittest.mock import patch
from rest_framework import status
from tests.base import PetCareAPITestCase
from apps.vaccinations.models import VaccinationEvent, VaccinationPlan
from integrations.inventory_client import InventoryUnavailable


class VaccinationTests(PetCareAPITestCase):
    def test_create_plan_replaces_previous_and_schedule_statuses(self):
        self.auth(self.vet_user)
        first = self.client.post(f'/api/v1/pets/{self.pet.id}/vaccination-plan/', {'items':[{'vaccine_name':'Rabia','scheduled_date':(date.today()-timedelta(days=1)).isoformat()}]}, format='json')
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(f'/api/v1/pets/{self.pet.id}/vaccination-plan/', {'items':[{'vaccine_name':'Triple','scheduled_date':(date.today()+timedelta(days=10)).isoformat()}]}, format='json')
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VaccinationPlan.objects.filter(patient=self.pet, is_active=True).count(), 1)
        schedule = self.client.get(f'/api/v1/pets/{self.pet.id}/vaccination-plan/schedule/')
        self.assertEqual(schedule.status_code, status.HTTP_200_OK)
        self.assertEqual(schedule.data['results'][0]['status'], 'PENDING')

    def test_only_vet_can_create_plan_and_event_required_fields(self):
        self.auth(self.owner_user)
        forbidden = self.client.post(f'/api/v1/pets/{self.pet.id}/vaccination-plan/', {'items':[]}, format='json')
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.vet_user)
        bad = self.client.post(f'/api/v1/pets/{self.pet.id}/vaccination-events/', {'vaccine_name':'Rabia'}, format='json')
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('integrations.inventory_client.InventoryClient.check_availability')
    @patch('integrations.inventory_client.InventoryClient.deduct_stock')
    def test_register_event_with_supply_discount(self, deduct, check):
        check.return_value = {'supply_id':'11111111-1111-1111-1111-111111111111'}
        deduct.return_value = check.return_value
        self.auth(self.vet_user)
        res = self.client.post(f'/api/v1/pets/{self.pet.id}/vaccination-events/', {
            'vaccine_name':'Rabia',
            'applied_date':date.today().isoformat(),
            'batch_number':'LOT-1',
            'supply_id':'11111111-1111-1111-1111-111111111111',
            'quantity_used':'1',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(deduct.called)
        self.assertEqual(str(deduct.call_args.kwargs['ref_id']), res.data['id'])


    def test_global_vaccination_viewsets_are_not_routed(self):
        self.auth(self.vet_user)
        self.assertEqual(self.client.get('/api/v1/vaccination-plans/').status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get('/api/v1/vaccination-events/').status_code, status.HTTP_404_NOT_FOUND)

    @patch('integrations.inventory_client.InventoryClient.check_availability')
    def test_register_event_inventory_unavailable_marks_pending_sync(self, check):
        check.side_effect = InventoryUnavailable('Backend 2 no disponible')
        self.auth(self.vet_user)
        res = self.client.post(f'/api/v1/pets/{self.pet.id}/vaccination-events/', {
            'vaccine_name':'Rabia',
            'applied_date':date.today().isoformat(),
            'batch_number':'LOT-2',
            'supply_id':'11111111-1111-1111-1111-111111111111',
            'quantity_used':'1',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['sync_status'], VaccinationEvent.SyncStatus.PENDING_SYNC)
