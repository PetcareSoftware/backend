import uuid
from django.db import models
from apps.common.models import BaseModel
from apps.owners.models import Owner


class ActivePetManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Species(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'species'
        ordering = ['name']

    def __str__(self):
        return self.name


class Breed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    species = models.ForeignKey(Species, db_column='species_id', on_delete=models.PROTECT, related_name='breeds')
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'breeds'
        ordering = ['species__name', 'name']
        constraints = [models.UniqueConstraint(fields=['species', 'name'], name='unique_breed_per_species')]

    def __str__(self):
        return f'{self.name} ({self.species.name})'


class Pet(BaseModel):
    SEX_CHOICES = (('M', 'Macho'), ('F', 'Hembra'))
    owner = models.ForeignKey(Owner, db_column='owner_id', on_delete=models.PROTECT, related_name='pets')
    breed = models.ForeignKey(Breed, db_column='breed_id', on_delete=models.PROTECT, related_name='pets')
    name = models.CharField(max_length=100)
    birth_date = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    microchip_id = models.CharField(max_length=100, unique=True, blank=True, null=True)

    objects = ActivePetManager()
    all_objects = models.Manager()

    class Meta:
        db_table = 'patients'
        ordering = ['name']

    def __str__(self):
        return self.name
