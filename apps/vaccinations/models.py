import uuid
from django.db import models
from apps.pets.models import Pet


class VaccinationPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Pet, db_column='patient_id', on_delete=models.CASCADE, related_name='vaccination_plans')
    created_by = models.ForeignKey('users.Veterinarian', db_column='created_by_id', on_delete=models.PROTECT, related_name='vaccination_plans')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vaccination_plans'


class VaccinationPlanItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(VaccinationPlan, db_column='plan_id', on_delete=models.CASCADE, related_name='items')
    vaccine_name = models.CharField(max_length=200)
    scheduled_date = models.DateField()
    supply_id = models.UUIDField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'vaccination_plan_items'
        ordering = ['scheduled_date']


class VaccinationEvent(models.Model):
    class SyncStatus(models.TextChoices):
        SYNCED = 'SYNCED', 'Sincronizado'
        PENDING_SYNC = 'PENDING_SYNC', 'Pendiente de sincronización'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Pet, db_column='patient_id', on_delete=models.CASCADE, related_name='vaccination_events')
    plan_item = models.ForeignKey(VaccinationPlanItem, db_column='plan_item_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    created_by = models.ForeignKey('users.Veterinarian', db_column='created_by_id', on_delete=models.PROTECT, related_name='vaccination_events')
    vaccine_name = models.CharField(max_length=200)
    applied_date = models.DateField()
    batch_number = models.CharField(max_length=100)
    dose = models.CharField(max_length=100, blank=True, null=True)
    next_due_date = models.DateField(blank=True, null=True)
    supply_id = models.UUIDField(blank=True, null=True)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sync_status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.SYNCED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vaccination_events'
        ordering = ['-applied_date']
