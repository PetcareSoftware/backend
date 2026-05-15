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