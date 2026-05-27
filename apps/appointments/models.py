from django.db import models

# Create your models here.

class Appointment(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    veterinarian = models.ForeignKey('users.Veterinarian', on_delete=models.CASCADE, related_name='appointments')
    reason_for_visit = models.TextField(help_text="Motivo de la consulta")
    appointment_date = models.DateTimeField()
    def __str__(self):
        return f"Cita el {self.appointment_date} - Paciente ID: {self.patient_id}"