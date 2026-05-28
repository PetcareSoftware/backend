from concurrent.futures import ThreadPoolExecutor
from datetime import date, time, timedelta
from threading import Barrier

from django.db import close_old_connections, connection
from django.test import TransactionTestCase
from unittest import skipIf
from rest_framework import status

from apps.appointments.models import Appointment
from apps.appointments.services import AppointmentService
from apps.common.exceptions import BusinessRuleError, SlotNotAvailableError
from apps.common.roles import OWNER, VET
from apps.owners.models import Owner
from apps.pets.models import Breed, Species
from apps.pets.services import PetService
from apps.schedules.models import TimeSlot
from apps.users.models import ClinicalStaff, Role, User, Veterinarian


@skipIf(
    connection.vendor == 'sqlite',
    'La prueba de select_for_update requiere PostgreSQL. No basta con desarrollo local SQLite; debe ejecutarse en CI con PostgreSQL antes del merge.',
)
class AppointmentConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        Role.objects.get_or_create(name=OWNER)
        Role.objects.get_or_create(name=VET)
        self.owner_user = User.objects.create_user(
            email='concurrent-owner@test.com', password='Password123!', first_name='Owner', last_name='Concurrent', role=OWNER
        )
        self.owner = Owner.objects.create(user=self.owner_user, dni='V-C1')
        self.vet_user = User.objects.create_user(
            email='concurrent-vet@test.com', password='Password123!', first_name='Vet', last_name='Concurrent', role=VET
        )
        self.staff = ClinicalStaff.objects.create(user=self.vet_user, employee_id='EC-1')
        self.vet = Veterinarian.objects.create(user=self.staff, license_number='LIC-C1', specialty='General')
        self.species = Species.objects.create(name='Perro')
        self.breed = Breed.objects.create(species=self.species, name='Labrador')
        self.pet = PetService.create_pet_for_owner(self.owner, {'name': 'Max', 'breed': self.breed, 'sex': 'M'})
        self.slot = TimeSlot.objects.create(
            vet=self.vet,
            date=date.today() + timedelta(days=1),
            start_time=time(8, 0),
            end_time=time(8, 30),
            status=TimeSlot.Status.FREE,
        )

    def test_two_concurrent_requests_same_slot_one_201_one_409(self):
        barrier = Barrier(2)

        def attempt():
            close_old_connections()
            barrier.wait(timeout=5)
            try:
                actor = User.objects.get(id=self.owner_user.id)
                vet = Veterinarian.objects.select_related('user__user').get(user_id=self.vet.user_id)
                AppointmentService.create(
                    actor=actor,
                    pet_id=self.pet.id,
                    vet=vet,
                    slot_id=self.slot.id,
                    reason='Concurrencia',
                )
                return status.HTTP_201_CREATED
            except (SlotNotAvailableError, BusinessRuleError) as exc:
                return exc.status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: attempt(), range(2)))

        self.assertEqual(results.count(status.HTTP_201_CREATED), 1)
        self.assertEqual(results.count(status.HTTP_409_CONFLICT), 1)
        self.assertEqual(Appointment.objects.filter(slot=self.slot).count(), 1)
