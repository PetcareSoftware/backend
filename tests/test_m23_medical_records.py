from datetime import date, time, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch
from rest_framework import status
from tests.base import PetCareAPITestCase
from apps.appointments.models import Appointment
from apps.medical_records.models import Consultation, SupplyUsed
from apps.schedules.models import TimeSlot
from integrations.inventory_client import InventoryClient


class MedicalRecordsTests(PetCareAPITestCase):
    def today_appointment(self):
        slot = TimeSlot.objects.create(
            vet=self.vet,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(9, 30),
            status=TimeSlot.Status.BOOKED,
        )
        return Appointment.objects.create(
            pet=self.pet,
            vet=self.vet,
            slot=slot,
            reason='Consulta clínica',
            status=Appointment.Status.SCHEDULED,
            scheduled_at=timezone.now(),
        )

    def checked_in_appointment(self):
        appointment = self.today_appointment()
        self.auth(self.receptionist)
        self.client.post(f'/api/v1/appointments/{appointment.id}/check-in/')
        return Appointment.objects.get(id=appointment.id)

    def register_consultation(self):
        appt = self.checked_in_appointment()
        self.auth(self.vet_user)
        res = self.client.post(f'/api/v1/appointments/{appt.id}/consultations/', {'diagnosis':'Otitis','clinical_notes':'Nota interna'}, format='json')
        return res

    def test_medical_record_owner_filtered_and_foreign_403(self):
        self.register_consultation()
        self.auth(self.vet_user)
        vet = self.client.get(f'/api/v1/pets/{self.pet.id}/medical-record/')
        self.assertEqual(vet.status_code, status.HTTP_200_OK)
        self.assertEqual(vet.data['consultations'][0]['clinical_notes'], 'Nota interna')
        self.auth(self.owner_user)
        owner = self.client.get(f'/api/v1/pets/{self.pet.id}/medical-record/')
        self.assertEqual(owner.status_code, status.HTTP_200_OK)
        self.assertIsNone(owner.data['consultations'][0]['clinical_notes'])
        other = self.client.get(f'/api/v1/pets/{self.other_pet.id}/medical-record/')
        self.assertEqual(other.status_code, status.HTTP_403_FORBIDDEN)

    def test_new_pet_record_empty_and_summary(self):
        self.auth(self.owner_user)
        res = self.client.get(f'/api/v1/pets/{self.pet.id}/medical-record/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['consultations'], [])
        summary = self.client.get(f'/api/v1/pets/{self.pet.id}/medical-record/summary/')
        self.assertEqual(summary.status_code, status.HTTP_200_OK)

    def test_register_consultation_rules_and_signal_completes(self):
        # scheduled -> 422
        created = self.create_appointment()
        appointment_id = created.data['id']
        self.auth(self.vet_user)
        scheduled = self.client.post(f'/api/v1/appointments/{appointment_id}/consultations/', {'diagnosis':'X'}, format='json')
        self.assertEqual(scheduled.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        # checked-in -> 201 and completed
        res = self.register_consultation()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        appt = Appointment.objects.get(id=res.data['appointment_id'])
        self.assertEqual(appt.status, Appointment.Status.COMPLETED)
        # duplicate -> 409
        dup = self.client.post(f'/api/v1/appointments/{appt.id}/consultations/', {'diagnosis':'Otra'}, format='json')
        self.assertEqual(dup.status_code, status.HTTP_409_CONFLICT)

    def test_other_vet_403_and_missing_diagnosis_400(self):
        appt = self.checked_in_appointment()
        self.auth(self.other_vet_user)
        res = self.client.post(f'/api/v1/appointments/{appt.id}/consultations/', {'diagnosis':'X'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.vet_user)
        res = self.client.post(f'/api/v1/appointments/{appt.id}/consultations/', {}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_consultation_within_and_after_24h(self):
        res = self.register_consultation()
        cid = res.data['id']
        patch = self.client.patch(f'/api/v1/consultations/{cid}/', {'diagnosis':'Actualizado'}, format='json')
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        consultation = Consultation.objects.get(id=cid)
        consultation.created_at = timezone.now() - timedelta(hours=25)
        consultation.save(update_fields=['created_at'])
        patch = self.client.patch(f'/api/v1/consultations/{cid}/', {'diagnosis':'Tarde'}, format='json')
        self.assertEqual(patch.status_code, status.HTTP_403_FORBIDDEN)

    def test_prescriptions_and_attachments(self):
        res = self.register_consultation()
        cid = res.data['id']
        ok = self.client.post(f'/api/v1/consultations/{cid}/prescriptions/', {'medicine_name':'Oticell','dosage':'2 gotas'}, format='json')
        self.assertEqual(ok.status_code, status.HTTP_201_CREATED)
        bad = self.client.post(f'/api/v1/consultations/{cid}/prescriptions/', {'dosage':'2 gotas'}, format='json')
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)
        file = SimpleUploadedFile('lab.pdf', b'%PDF-1.4', content_type='application/pdf')
        up = self.client.post(f'/api/v1/consultations/{cid}/attachments/', {'attachment_type':'LAB','file':file}, format='multipart')
        self.assertEqual(up.status_code, status.HTTP_201_CREATED)
        exe = SimpleUploadedFile('x.exe', b'bad', content_type='application/x-msdownload')
        bad_type = self.client.post(f'/api/v1/consultations/{cid}/attachments/', {'attachment_type':'LAB','file':exe}, format='multipart')
        self.assertEqual(bad_type.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('integrations.inventory_client.InventoryClient.check_availability')
    @patch('integrations.inventory_client.InventoryClient.deduct_stock')
    def test_supplies_used_synced(self, deduct, check):
        check.return_value = {'supply_id':'11111111-1111-1111-1111-111111111111','name':'Gasas','unit_cost':'2.00'}
        deduct.return_value = check.return_value
        res = self.register_consultation()
        cid = res.data['id']
        payload = {'supplies':[{'supply_id':'11111111-1111-1111-1111-111111111111','quantity':'1'}]}
        used = self.client.post(f'/api/v1/consultations/{cid}/supplies-used/', payload, format='json')
        self.assertEqual(used.status_code, status.HTTP_201_CREATED)
        self.assertEqual(used.data['results'][0]['sync_status'], SupplyUsed.SyncStatus.SYNCED)
        deduct.assert_called_once()
        self.assertEqual(str(deduct.call_args.kwargs['ref_id']), str(cid))

    def test_supplies_quantity_zero_and_non_numeric_400(self):
        res = self.register_consultation()
        cid = res.data['id']
        used = self.client.post(f'/api/v1/consultations/{cid}/supplies-used/', {'supplies':[{'supply_id':'11111111-1111-1111-1111-111111111111','quantity':'0'}]}, format='json')
        self.assertEqual(used.status_code, status.HTTP_400_BAD_REQUEST)
        bad = self.client.post(f'/api/v1/consultations/{cid}/supplies-used/', {'supplies':[{'supply_id':'11111111-1111-1111-1111-111111111111','quantity':'abc'}]}, format='json')
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)

    def test_global_medical_record_endpoint_does_not_expose_foreign_owner_record(self):
        self.auth(self.owner_user)
        res = self.client.get(f'/api/v1/medical-records/{self.other_pet.medical_record.id}/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_inventory_client_exposes_documented_contract(self):
        client = InventoryClient(base_url='http://backend2.test')
        self.assertTrue(callable(client.get_supply))
        self.assertTrue(callable(client.check_availability))
        self.assertTrue(callable(client.deduct_stock))
