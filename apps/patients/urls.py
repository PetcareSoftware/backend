from django.urls import path
from . import views

urlpatterns = [
    path('<int:pet_id>/medical-record/summary/', views.pet_medical_record_summary, name='pet-medical-record-summary'),
    path('<int:pet_id>/medical-record/', views.pet_medical_record, name='pet-medical-record'),
    path('<int:pet_id>/vaccination-plan/schedule/', views.pet_vaccination_schedule, name='pet-vaccination-schedule'),
    path('<int:pet_id>/vaccination-events/', views.pet_vaccination_events, name='pet-vaccination-events'),
]
