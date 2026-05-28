from django.contrib import admin
from .models import TimeSlot, VetSchedule
admin.site.register(VetSchedule)
admin.site.register(TimeSlot)
