from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
# Create your models here.

class Appointment(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    veterinarian = models.ForeignKey('users.Veterinarian', on_delete=models.CASCADE, related_name='appointments')
    reason_for_visit = models.TextField(help_text="Motivo de la consulta")
    appointment_date = models.DateTimeField()
    def __str__(self):
        return f"Cita el {self.appointment_date} - Paciente ID: {self.patient_id}"
    
class VetSchedule(models.Model):
    vet = models.ForeignKey('users.Veterinarian', on_delete=models.CASCADE, related_name='schedules')
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        super().clean()
        # 1. Fecha fin no anterior a fecha inicio
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

        # 2. Los TimeSlots asociados deben estar dentro del rango (si ya existe la instancia)
        if self.pk:
            slots_out_of_range = self.time_slots.filter(
                Q(start_time__date__lt=self.start_date) |
                Q(end_time__date__gt=self.end_date)
            )
            if slots_out_of_range.exists():
                raise ValidationError(
                    "Las franjas horarias (TimeSlots) deben estar contenidas dentro del intervalo de fecha de la agenda."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)