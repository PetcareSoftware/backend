from django.db import transaction
from django.core.exceptions import ValidationError
from apps.users.models import Veterinarian
from apps.appointments.models import Appointment

def schedule_secure_appointment(veterinarian_id,patient_id,date,reason):
    """Servicio transaccional (ACID) para programar citas evitando conflictos simultáneos.Utiliza Pessimistic Locking para la serialización de solicitudes
    """
    with transaction.atomic():
        try:
            vet = Veterinarian.objects.select_for_update().get(id = veterinarian_id)
        except Veterinarian.DoesNotExist:
            raise ValidationError(f"El veterinario especificado de id {veterinarian_id} no existe")
        collision = Appointment.objects.filter(veterinarian = vet, appointment_date = date).exists()
        if collision:
            raise ValidationError("Error de concurrencia: La mimsma fecha de cita fue registrada por otro usuario.\nPor favor seleccione otra fecha")
        new_appointment = Appointment.objects.create(veterinarian = vet,patient = patient_id,appointment_date= date,reason_for_visit =reason)
    return new_appointment

