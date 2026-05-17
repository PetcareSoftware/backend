from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsumoViewSet # Asegúrate de que este nombre coincida con tu vista

router = DefaultRouter()
router.register(r'insumos', InsumoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]