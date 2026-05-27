from django.db import models
from apps.users.models import User  # Importamos el modelo User

# Tabla propietarios
class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tax_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    staff_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Owner: {self.user.email}"