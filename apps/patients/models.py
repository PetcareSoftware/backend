from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    species_breed = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
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
        db_table = 'clinical_records'

    def __str__(self):
        return f"Historial Clínico - {self.patient.name}"