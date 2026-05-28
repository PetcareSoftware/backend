from django.contrib import admin
from .models import VaccinationEvent, VaccinationPlan, VaccinationPlanItem
admin.site.register(VaccinationPlan)
admin.site.register(VaccinationPlanItem)
admin.site.register(VaccinationEvent)
