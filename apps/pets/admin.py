from django.contrib import admin
from .models import Breed, Pet, Species
admin.site.register(Species)
admin.site.register(Breed)
admin.site.register(Pet)
