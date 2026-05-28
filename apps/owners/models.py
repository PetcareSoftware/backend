from django.db import models
from apps.users.models import User, NaturalPerson

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    natural_person = models.OneToOneField(NaturalPerson, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    staff_notes = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)
    # tax_id eliminado
    # phone, address, dni eliminados (ahora en NaturalPerson)

    def __str__(self):
        return f"Owner: {self.user.email}"