from datetime import date
from celery import shared_task
from apps.users.models import Veterinarian
from .services import AvailabilityService


@shared_task
def generate_slots_for_vet_range(vet_user_id, date_from_iso, date_to_iso):
    vet = Veterinarian.objects.get(user_id=vet_user_id)
    return len(AvailabilityService.generate_slots(vet, date.fromisoformat(date_from_iso), date.fromisoformat(date_to_iso)))
