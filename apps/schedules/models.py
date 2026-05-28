import uuid
from django.db import models
from django.db.models import Q


class VetSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vet = models.ForeignKey('users.Veterinarian', db_column='vet_id', on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.SmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_min = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'vet_schedules'
        constraints = [
            models.CheckConstraint(condition=Q(day_of_week__gte=0) & Q(day_of_week__lte=6), name='schedule_day_of_week_0_6'),
            models.CheckConstraint(condition=Q(slot_duration_min__gt=0), name='schedule_duration_positive'),
        ]


class TimeSlot(models.Model):
    class Status(models.TextChoices):
        FREE = 'FREE', 'Libre'
        BOOKED = 'BOOKED', 'Reservado'
        BLOCKED = 'BLOCKED', 'Bloqueado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vet = models.ForeignKey('users.Veterinarian', db_column='vet_id', on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.FREE)

    class Meta:
        db_table = 'time_slots'
        ordering = ['date', 'start_time']
        constraints = [models.UniqueConstraint(fields=['vet', 'date', 'start_time', 'end_time'], name='unique_timeslot_per_vet_date_time')]
