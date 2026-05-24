from django.db import models


class Pet(models.Model):
    """Mascota registrada en el sistema, asociada a un propietario."""

    class Species(models.TextChoices):
        DOG = 'DOG', 'Perro'
        CAT = 'CAT', 'Gato'
        BIRD = 'BIRD', 'Ave'
        RABBIT = 'RABBIT', 'Conejo'
        OTHER = 'OTHER', 'Otro'

    owner = models.ForeignKey(
        'owners.Owner',
        on_delete=models.CASCADE,
        related_name='pets',
    )
    name = models.CharField(max_length=100)
    species = models.CharField(
        max_length=10,
        choices=Species.choices,
        default=Species.OTHER,
    )
    breed = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(
        max_length=1,
        choices=[('M', 'Macho'), ('F', 'Hembra')],
        blank=True,
    )
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'

    def __str__(self):
        return f'{self.name} ({self.owner})'


class MedicalRecord(models.Model):
    """Expediente clínico asociado a una mascota. Se crea automáticamente al registrar la mascota."""

    pet = models.OneToOneField(
        Pet,
        on_delete=models.CASCADE,
        related_name='medical_record',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Expediente Clínico'
        verbose_name_plural = 'Expedientes Clínicos'

    def __str__(self):
        return f'MedicalRecord({self.pet.name})'
