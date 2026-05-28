from django.db import transaction
from apps.common.exceptions import BusinessRuleError
from apps.medical_records.models import MedicalRecord
from .models import Pet


class PetService:
    @staticmethod
    @transaction.atomic
    def create_pet_for_owner(owner, data):
        data.pop('owner_id', None)
        pet = Pet.all_objects.create(owner=owner, **data)
        MedicalRecord.objects.create(patient=pet)
        return pet

    @staticmethod
    @transaction.atomic
    def soft_delete(pet):
        from apps.appointments.models import Appointment
        active = Appointment.objects.filter(
            pet=pet,
            status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED, Appointment.Status.CHECKED_IN],
        ).exists()
        if active:
            raise BusinessRuleError('No se puede eliminar una mascota con citas activas.', status_code=409)
        pet.is_deleted = True
        pet.save(update_fields=['is_deleted'])
        return pet
