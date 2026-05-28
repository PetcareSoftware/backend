import os
import sys
from datetime import date, time, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


def ensure_password(user, password):
    if not user.has_usable_password():
        user.set_password(password)
        user.save()


def main():
    import django

    django.setup()

    from apps.common.roles import MANAGER, OWNER, RECEPTIONIST, TECH_VET, VET
    from apps.owners.models import Owner
    from apps.pets.models import Breed, Species
    from apps.schedules.models import VetSchedule
    from apps.schedules.services import AvailabilityService
    from apps.users.models import ClinicalStaff, Role, User, Veterinarian

    for role in [OWNER, RECEPTIONIST, VET, TECH_VET, MANAGER]:
        Role.objects.get_or_create(name=role)

    owner_role = Role.objects.get(name=OWNER)
    vet_role = Role.objects.get(name=VET)
    rec_role = Role.objects.get(name=RECEPTIONIST)

    owner, _ = User.objects.get_or_create(
        email='owner@petcare.com',
        defaults={'first_name': 'Juan', 'last_name': 'Perez', 'role': owner_role},
    )
    ensure_password(owner, 'Password123!')
    Owner.objects.get_or_create(
        user=owner,
        defaults={'phone': '+58 414 1234567', 'dni': 'V-12345678'},
    )

    vet_user, _ = User.objects.get_or_create(
        email='vet@petcare.com',
        defaults={'first_name': 'Carlos', 'last_name': 'Mendez', 'role': vet_role},
    )
    ensure_password(vet_user, 'Password123!')
    staff, _ = ClinicalStaff.objects.get_or_create(
        user=vet_user,
        defaults={'employee_id': 'VET-001'},
    )
    vet, _ = Veterinarian.objects.get_or_create(
        user=staff,
        defaults={'license_number': 'LIC-001', 'specialty': 'Medicina General'},
    )

    rec, _ = User.objects.get_or_create(
        email='recepcion@petcare.com',
        defaults={'first_name': 'Maria', 'last_name': 'Gonzalez', 'role': rec_role},
    )
    ensure_password(rec, 'Password123!')

    species, _ = Species.objects.get_or_create(name='Perro')
    Breed.objects.get_or_create(species=species, name='Labrador Retriever')

    schedule_defaults = {
        'start_time': time(8, 0),
        'end_time': time(12, 0),
        'slot_duration_min': 30,
    }
    VetSchedule.objects.get_or_create(
        vet=vet,
        day_of_week=date.today().weekday(),
        defaults=schedule_defaults,
    )
    AvailabilityService.generate_slots(vet, date.today(), date.today() + timedelta(days=7))
    print('Seed listo.')


if __name__ == '__main__':
    main()
