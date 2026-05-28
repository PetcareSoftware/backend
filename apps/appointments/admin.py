from django.contrib import admin
from .models import Appointment, WaitingListEntry
admin.site.register(Appointment)
admin.site.register(WaitingListEntry)
