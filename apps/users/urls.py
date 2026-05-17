from django.urls import path
from .views import RecepcionistaTestView

urlpatterns = [
    path('test-recepcionista/', RecepcionistaTestView.as_view(), name='test-recepcionista'),
]   