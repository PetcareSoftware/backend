import uuid
from django.db import models
from django.db.models import Q


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Agendada'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        CHECKED_IN = 'CHECKED_IN', 'Paciente llegó'
        COMPLETED = 'COMPLETED', 'Completada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    ACTIVE_STATUSES = [Status.SCHEDULED, Status.CONFIRMED, Status.CHECKED_IN]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pet = models.ForeignKey('pets.Pet', db_column='patient_id', on_delete=models.PROTECT, related_name='appointments')
    vet = models.ForeignKey('users.Veterinarian', db_column='vet_id', on_delete=models.PROTECT, related_name='appointments')
    # FK, no OneToOne: permite reutilizar el slot si la cita histórica quedó CANCELLED.
    slot = models.ForeignKey('schedules.TimeSlot', db_column='slot_id', on_delete=models.PROTECT, related_name='appointments')
    reason = models.CharField(max_length=500)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True, null=True)
    scheduled_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-scheduled_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slot'],
                condition=Q(status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN']),
                name='unique_active_appointment_per_slot',
            ),
            models.UniqueConstraint(
                fields=['pet', 'slot'],
                condition=Q(status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN']),
                name='unique_active_pet_appointment_per_slot',
            ),
        ]


class WaitingListEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.OneToOneField(Appointment, db_column='appointment_id', on_delete=models.CASCADE, related_name='waiting_entry')
    vet = models.ForeignKey('users.Veterinarian', db_column='vet_id', on_delete=models.PROTECT, related_name='waiting_list_entries')
    queue_date = models.DateField()
    position = models.IntegerField()
    arrived_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'waiting_list_entries'
        ordering = ['arrived_at']
        constraints = [
            models.UniqueConstraint(fields=['vet', 'queue_date', 'position'], name='unique_waiting_position_per_vet_date'),
        ]
        indexes = [models.Index(fields=['vet', 'queue_date', 'called_at'], name='waiting_vet_date_call_idx')]
