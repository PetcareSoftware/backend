import uuid
from django.db import models
from django.utils import timezone


def attachment_upload_path(instance, filename):
    return f'attachments/{instance.consultation_id}/{filename}'


class MedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField('pets.Pet', db_column='patient_id', on_delete=models.PROTECT, related_name='medical_record')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medical_records'


class Consultation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(MedicalRecord, db_column='medical_record_id', on_delete=models.PROTECT, related_name='consultations')
    appointment = models.OneToOneField('appointments.Appointment', db_column='appointment_id', on_delete=models.PROTECT, related_name='consultation')
    vet = models.ForeignKey('users.Veterinarian', db_column='vet_id', on_delete=models.PROTECT, related_name='consultations')
    diagnosis = models.TextField()
    clinical_notes = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultations'
        ordering = ['-date', '-created_at']


class Treatment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, db_column='consultation_id', on_delete=models.CASCADE, related_name='treatments')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    duration_days = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'treatments'


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, db_column='consultation_id', on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=200)
    frequency = models.CharField(max_length=200, blank=True, null=True)
    duration_days = models.IntegerField(blank=True, null=True)
    supply_id = models.UUIDField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prescriptions'


class MedicalAttachment(models.Model):
    class AttachmentType(models.TextChoices):
        XRAY = 'XRAY', 'Radiografía'
        LAB = 'LAB', 'Laboratorio'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, db_column='consultation_id', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=attachment_upload_path)
    attachment_type = models.CharField(max_length=10, choices=AttachmentType.choices)
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medical_attachments'


class SupplyUsed(models.Model):
    class SyncStatus(models.TextChoices):
        SYNCED = 'SYNCED', 'Sincronizado'
        PENDING_SYNC = 'PENDING_SYNC', 'Pendiente de sincronización'
        FAILED = 'FAILED', 'Fallido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, db_column='consultation_id', on_delete=models.CASCADE, related_name='supplies_used')
    supply_id = models.UUIDField()
    supply_name = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sync_status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING_SYNC)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supply_used'
