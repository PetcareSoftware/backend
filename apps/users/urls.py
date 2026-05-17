from django.urls import path
from .views import RegistroUsuarioView, LoginView, PanelGerenteView, VerificarUsuarioView

urlpatterns =[
    #ruta para registrar un usuario
    path('register/', RegistroUsuarioView.as_view(), name='user-register'),
    #ruta para iniciar sesion
    path('login',LoginView.as_view(), name = 'user-login'),
    #ruta protegida de autorizacion(solo geretes)
    path('panel-gerente/', PanelGerenteView.as_view(), name='panel-gerente'),
    #ruta para backend 1
    path('me/', VerificarUsuarioView.as_view(), name='user-me'),
]