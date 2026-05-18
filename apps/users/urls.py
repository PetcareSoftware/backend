
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsumoViewSet 
from .views import RegistroUsuarioView, LoginView, PanelGerenteView, VerificarUsuarioView
from .views import RecepcionistaTestView
router = DefaultRouter()
router.register(r"insumos", InsumoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('test-recepcionista/', RecepcionistaTestView.as_view(), name='test-recepcionista'),
    #ruta para registrar un usuario
    path('register/', RegistroUsuarioView.as_view(), name='user-register'),
    #ruta para iniciar sesion
    path('login',LoginView.as_view(), name = 'user-login'),
    #ruta protegida de autorizacion(solo geretes)
    path('panel-gerente/', PanelGerenteView.as_view(), name='panel-gerente'),
    #ruta para backend 1
    path('me/', VerificarUsuarioView.as_view(), name='user-me'),
]








