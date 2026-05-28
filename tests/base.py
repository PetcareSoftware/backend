from datetime import date, time, timedelta
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from apps.common.roles import OWNER, RECEPTIONIST, VET, MANAGER
from apps.users.models import ClinicalStaff, Role, User, Veterinarian
from apps.owners.models import Owner
from apps.pets.models import Breed, Species
from apps.pets.services import PetService
from apps.schedules.models import TimeSlot, VetSchedule
from apps.schedules.services import AvailabilityService
from apps.users.tokens import build_token_pair


class PetCareAPITestMixin:

    def setUp(self):
        for role in [OWNER, RECEPTIONIST, VET, MANAGER]:
            Role.objects.get_or_create(name=role)
        self.owner_user = User.objects.create_user(email='owner@test.com', password='Password123!', first_name='Owner', last_name='Uno', role=OWNER)
        self.owner = Owner.objects.create(user=self.owner_user, dni='V-1')
        self.other_owner_user = User.objects.create_user(email='other@test.com', password='Password123!', first_name='Owner', last_name='Dos', role=OWNER)
        self.other_owner = Owner.objects.create(user=self.other_owner_user, dni='V-2')
        self.receptionist = User.objects.create_user(email='recep@test.com', password='Password123!', first_name='Recep', last_name='Uno', role=RECEPTIONIST)
        self.manager = User.objects.create_user(email='manager@test.com', password='Password123!', first_name='Manager', last_name='Uno', role=MANAGER)
        self.vet_user = User.objects.create_user(email='vet@test.com', password='Password123!', first_name='Vet', last_name='Uno', role=VET)
        self.staff = ClinicalStaff.objects.create(user=self.vet_user, employee_id='E-1')
        self.vet = Veterinarian.objects.create(user=self.staff, license_number='LIC-1', specialty='General')
        self.other_vet_user = User.objects.create_user(email='vet2@test.com', password='Password123!', first_name='Vet', last_name='Dos', role=VET)
        self.other_staff = ClinicalStaff.objects.create(user=self.other_vet_user, employee_id='E-2')
        self.other_vet = Veterinarian.objects.create(user=self.other_staff, license_number='LIC-2', specialty='General')
        self.species = Species.objects.create(name='Perro')
        self.breed = Breed.objects.create(species=self.species, name='Labrador')
        self.pet = PetService.create_pet_for_owner(self.owner, {'name':'Max','breed':self.breed,'sex':'M'})
        self.other_pet = PetService.create_pet_for_owner(self.other_owner, {'name':'Luna','breed':self.breed,'sex':'F'})
        self.tomorrow = date.today() + timedelta(days=1)
        self.schedule = VetSchedule.objects.create(vet=self.vet, day_of_week=self.tomorrow.weekday(), start_time=time(8,0), end_time=time(10,0), slot_duration_min=30)
        AvailabilityService.generate_slots(self.vet, self.tomorrow, self.tomorrow)
        self.slot = TimeSlot.objects.filter(vet=self.vet, date=self.tomorrow, status=TimeSlot.Status.FREE).first()
        self.client = APIClient()

    def auth(self, user):
        token = build_token_pair(user)['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def create_appointment(self, user=None, pet=None, slot=None):
        self.auth(user or self.owner_user)
        return self.client.post('/api/v1/appointments/', {
            'pet_id': str((pet or self.pet).id),
            'vet_id': str(self.vet.user_id),
            'slot_id': str((slot or self.slot).id),
            'reason': 'Consulta',
        }, format='json')


class PetCareAPITestCase(PetCareAPITestMixin, TestCase):
    pass


class PetCareAPITransactionTestCase(PetCareAPITestMixin, TransactionTestCase):
    pass
