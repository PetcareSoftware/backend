from django.db import models
from django.conf import settings

# Create your models here.

class ClinicalStaff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clinical_staff')
    cargo = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Staff - Usuario ID: {self.user_id}"

class Veterinarian(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='veterinarian')
    especialidad = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Veterinario - Usuario ID: {self.user_id}"