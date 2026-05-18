from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# El router se encarga de crear las rutas automáticas para el InsumoViewSet
router = DefaultRouter()
router.register(r'insumos', views.InsumoViewSet, basename='insumo')

urlpatterns = [
    # Tus rutas de seguridad
    path('recepcionista/', views.RecepcionistaTestView.as_view(), name='recepcionista_test'),
    path('gerente/', views.PanelGerenteView.as_view(), name='panel_gerente'),
    path('me/', views.VerificarUsuarioView.as_view(), name='verificar_usuario'),
    
    # La ruta de tu compañero
    path('', include(router.urls)),
]








