from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    species_breed = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    birth_date = models.DateField()
    current_weight = models.FloatField()
    owner = models.ForeignKey('owners.Owner',on_delete=models.SET_NULL,null=True)
    physical_marks = models.CharField(max_length=255)
    microchip_id = models.CharField(max_length=50)
    reproductive_status = models.CharField(max_length=50)

    class Meta:
        db_table = 'patient'


class ClinicalRecords(models.Model):
    patient = models.OneToOneField(Patient,on_delete=models.CASCADE)
    opened_at = models.DateField()
    allergies_history = models.TextField()
    medical_alerts = models.TextField()

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