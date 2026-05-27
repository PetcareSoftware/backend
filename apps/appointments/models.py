from django.db import models

# Create your models here.

class VetSchedule(models.Model):
    vet = models.ForeignKey('users.Veterinarian', on_delete=models.CASCADE, related_name='schedules')
    start_date = models.DateField()
    end_date = models.DateField()

class TimeSlot(models.Model):
    STATUS_CHOICES = [
        ('FREE', 'Libre'),
        ('BOOKED', 'Reservado'),
        ('BLOCKED', 'Bloqueado')
    ]
    schedule = models.ForeignKey(VetSchedule, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='FREE')

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Programada'),
        ('CONFIRMED', 'Confirmada'),
        ('CHECKED_IN', 'En Sala'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada')
    ]
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    reason_for_visit = models.TextField(help_text="Motivo de la consulta")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED')
    checked_in_at = models.DateTimeField(null=True, blank=True)

class WaitingListEntry(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Baja'), ('MEDIUM', 'Media'), ('HIGH', 'Alta'), ('CRITICAL', 'Crítica')
    ]
    STATUS_CHOICES = [
        ('WAITING', 'Esperando'), ('ATTENDING', 'En Atención'), ('DONE', 'Finalizado'), ('ABANDONED', 'Abandonó')
    ]
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    priority_level = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAITING')