from django.db import models
from apps.users.models import User, NaturalPerson

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    tax_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    staff_notes = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Owner: {self.user.email}"