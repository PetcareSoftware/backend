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
    gender = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    coat_type = models.CharField(max_length=50,null=True,blank=True)
    microchip_number = models.CharField(max_length=50,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'patients'

    def __str__(self):
        return f"{self.name} - {self.breed.name}"



class MedicalRecords(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medical_records'

class Consultation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(MedicalRecords, on_delete=models.CASCADE)
    veterinarian = models.ForeignKey('users.Veterinarian', on_delete=models.PROTECT)
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL,null = True, blank=True)
    consultation_type = models.CharField(max_length=20)
    reason = models.TextField()
    weight = models.DecimalField(max_digits=6,decimal_places=2,null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2,null =True)
    heart_rate = models.IntegerField(default = None,null=True)
    clinical_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultations'
    
    def __str__(self):
        return f"Consulta {self.consultation_type} - Paciente: {self.medical_record.patient.name}"

class ClinicalProcedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation,on_delete=models.CASCADE)
    procedure_name = models.CharField(max_length=150)
    description = models.TextField(null = True,blank =True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    complications = models.TextField(null = True,blank =True)

    class Meta:
        db_table = 'clinical_procedures'

class Diagnoses(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20,editable=False,unique=True)
    name = models.CharField(max_length = 200)
    description = models.TextField(default=None,null = True)
    
    class Meta:
        db_table = 'diagnoses'

    def __str__(self):
        return f"[{self.code}] {self.name}"
class ConsultationDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete = models.CASCADE)
    diagnosis = models.ForeignKey(Diagnoses, on_delete=models.SET_NULL,null= True)  
    notes = models.TextField(default=None,null = True)

    class Meta:
        db_table ='consultation_details'
class Treatment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = 'treatments'

class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    class Meta:
        db_table = 'prescriptions'
class MedicalAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation,on_delete=models.CASCADE)
    file_url = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField()
    
    class Meta:
        db_table = 'medical_attachments'

class VaccinationPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient =  models.ForeignKey(Patient,on_delete=models.CASCADE)
    veterinarian = models.ForeignKey('users.Veterinarian', on_delete = models.PROTECT)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vaccination_plans'
class VaccinationPlanItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(VaccinationPlan,on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    target_age_days = models.IntegerField()
    class Meta:
        db_table = 'vaccination_plan_items'

class VaccinationDewormingEvents(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(VaccinationPlan,on_delete=models.CASCADE,null = True, blank=True)
    consultation = models.ForeignKey(Consultation,on_delete=models.CASCADE,null = True, blank=True)
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    applied_at = models.DateTimeField()
    next_due_date = models.DateField(null = True, blank=True)
    lot_number = models.CharField(max_length=50,null = True, blank=True)

    class Meta:
        db_table = 'vaccination_deworming_events'
