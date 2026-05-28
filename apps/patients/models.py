from django.db import models
import uuid

class Specie(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=50)
    class Meta:
        db_table = 'species'

class Breed(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable =False)
    species = models.ForeignKey(Specie,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    class Meta:
        db_table = 'breeds'
    def __str__(self):
        return f"{self.name} ({self.species.name})"
class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('owners.Owner', on_delete=models.PROTECT)
    breed = models.ForeignKey(Breed,on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    current_weight = models.FloatField()
    owner = models.ForeignKey('owners.Owner', on_delete=models.SET_NULL, null=True, related_name='patients')
    physical_marks = models.CharField(max_length=255, blank=True, null=True)
    microchip_id = models.CharField(max_length=50, blank=True, null=True)
    reproductive_status = models.CharField(max_length=50)

    class Meta:
        db_table = 'patients'

    def __str__(self):
        return self.name

class ClinicalRecord(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='clinical_record')
    opened_at = models.DateField(auto_now_add=True)
    allergies_history = models.TextField(blank=True, null=True)
    medical_alerts = models.TextField(blank=True, null=True)

    class Meta:
        db_table= 'clinical_records'

class VaccinationPlan(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='vaccination_plans')
    vet = models.ForeignKey('users.Veterinarian', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

class VaccinationPlanItem(models.Model):
    plan = models.ForeignKey(VaccinationPlan, on_delete=models.CASCADE, related_name='items')
    vaccine_name = models.CharField(max_length=100)
    target_age_days = models.IntegerField(help_text="Edad óptima sugerida en días")

class VaccinationDewormingEvent(models.Model):
    TYPE_CHOICES = [
        ('VACCINE', 'Vacuna'),
        ('DEWORMING', 'Desparasitante')
    ]
    plan = models.ForeignKey(VaccinationPlan, on_delete=models.SET_NULL, null=True, blank=True)
    # Como la app 'clinic' no está visible, referenciamos el modelo en texto para evitar errores
    consultation = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    dose = models.CharField(max_length=50)
    applied_date = models.DateField()
    sanitary_batch = models.CharField(max_length=100)
    next_due_date = models.DateField(null=True, blank=True)
