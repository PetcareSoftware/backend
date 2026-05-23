from django.urls import path
from . import views

urlpatterns = [
    # Vets
    path('vets/<int:vet_id>/slots/', views.vet_slots, name='vet-slots'),
    
    # Schedules
    path('schedules/calendar/', views.schedule_calendar, name='schedule-calendar'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/<int:id>/cancel/', views.appointment_cancel, name='appointment-cancel'),
    path('appointments/<int:id>/confirm/', views.appointment_confirm, name='appointment-confirm'),
    path('appointments/<int:id>/check-in/', views.appointment_check_in, name='appointment-checkin'),
    path('appointments/<int:id>/consultations/', views.appointment_consultations, name='appointment-consultations'),
    path('appointments/today/', views.appointments_today, name='appointments-today'),
    path('appointments/today/by-vet/<int:vet_id>/', views.appointments_today_by_vet, name='appointments-today-vet'),
    
    # Waiting List
    path('waiting-list/', views.waiting_list, name='waiting-list'),
    path('waiting-list/<int:id>/call-next/', views.waiting_list_call_next, name='waiting-list-call-next'),
    
    # Consultations
    path('consultations/<int:id>/supplies-used/', views.consultation_supplies_used, name='consultation-supplies'),
]
