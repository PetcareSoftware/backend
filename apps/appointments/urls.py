from django.urls import path
from . import views

urlpatterns = [
    # Vets
    path('vets/<int:vet_id>/slots/', views.vet_slots, name='vet-slots'),
    
    # Schedules
    path('schedules/calendar/', views.schedule_calendar, name='schedule-calendar'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/<int:appointment_id>/cancel/', views.appointment_cancel, name='appointment-cancel'),
    path('appointments/<int:appointment_id>/confirm/', views.appointment_confirm, name='appointment-confirm'),
    path('appointments/<int:appointment_id>/check-in/', views.appointment_check_in, name='appointment-checkin'),
    path('appointments/<int:appointment_id>/consultations/', views.appointment_consultations, name='appointment-consultations'),
    
    # Waiting List
    path('waiting-list/', views.waiting_list, name='waiting-list'),
    path('waiting-list/<int:queue_id>/call-next/', views.waiting_list_call_next, name='waiting-list-call-next'),
    
    # Consultations
    path('consultations/<int:consultation_id>/supplies-used/', views.consultation_supplies_used, name='consultation-supplies'),
]
