from django.contrib import admin
from .models import Consultation, MedicalAttachment, MedicalRecord, Prescription, SupplyUsed, Treatment
admin.site.register(MedicalRecord)
admin.site.register(Consultation)
admin.site.register(Treatment)
admin.site.register(Prescription)
admin.site.register(MedicalAttachment)
admin.site.register(SupplyUsed)
