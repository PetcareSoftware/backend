from django.urls import path
from . import views

urlpatterns = [
    # Tus rutas de seguridad (ajustadas a la nueva convención en inglés)
    path('receptionist/', views.ReceptionistTestView.as_view(), name='receptionist_test'),
    path('manager/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('me/', views.VerifyUserView.as_view(), name='verify_user'),
    
    # La ruta de tu compañero
    path('logs/', views.LogDashboardView.as_view(), name='log_entry_list'),
]