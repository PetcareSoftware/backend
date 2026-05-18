from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsumoViewSet 
from .views import RecepcionistaTestView
router = DefaultRouter()
router.register(r"insumos", InsumoViewSet)

urlpatterns = [
    path("", include(router.urls)),
     path('test-recepcionista/', RecepcionistaTestView.as_view(), name='test-recepcionista'),
]




