from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    species_breed = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    birth_date = models.DateField()
    current_weight = models.DecimalField(max_digits=6, decimal_places=2)
    owner = models.ForeignKey('owners.Owner', on_delete=models.SET_NULL, null=True)
    physical_marks = models.CharField(max_length=255)
    microchip_id = models.CharField(max_length=50)
    reproductive_status = models.CharField(max_length=50)

    class Meta:
        db_table = 'patients'

class ClinicalRecord(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    opened_at = models.DateField()
    allergies_history = models.TextField()
    medical_alerts = models.TextField()

    class Meta:
        db_table = 'clinical_records'

class Consultation(models.Model):
    anamnesis = models.TextField()
    clinical_findings = models.TextField()
    diagnosis = models.TextField()
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE)
    veterinarian = models.ForeignKey('users.Veterinarian', on_delete=models.SET_NULL, null=True)
    heart_rate = models.IntegerField()
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    prognosis = models.CharField(max_length=255)

    class Meta:
        db_table = 'consultations'

class Procedure(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    procedure_name = models.CharField(max_length=100)
    report_details = models.TextField()
    lead_veterinarian = models.ForeignKey('users.Veterinarian', on_delete=models.SET_NULL, null=True, related_name='procedimientos_liderados')
    assistant_tech = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='procedimientos_asistidos')
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    surgical_risk = models.CharField(max_length=50)

    class Meta:
        db_table = 'procedures'

class UsageDetails(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, null=True, blank=True)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('stock.Product', on_delete=models.SET_NULL, null=True)
    batch = models.ForeignKey('stock.Batch', on_delete=models.SET_NULL, null=True)
    quantity_used = models.DecimalField(max_digits=8, decimal_places=2)
    applied_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measure = models.CharField(max_length=50)

    class Meta:
        db_table = 'usage_details'