from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# El router se encarga de crear las rutas automáticas para el SupplyViewSet
router = DefaultRouter()
router.register(r'supplies', views.SupplyViewSet, basename='supply')

urlpatterns = [
    # Tus rutas de seguridad (ajustadas a la nueva convención en inglés)
    path('receptionist/', views.ReceptionistTestView.as_view(), name='receptionist_test'),
    path('manager/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('me/', views.VerifyUserView.as_view(), name='verify_user'),
    
    # La ruta de tu compañero
    path('', include(router.urls)),
    path('logs/', views.LogDashboardView.as_view(), name='log_entry_list'),
]