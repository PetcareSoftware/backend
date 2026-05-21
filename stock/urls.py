from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.stock.views import MedicalSupplyViewSet

router = DefaultRouter()
router.register(r'supplies', MedicalSupplyViewSet, basename='supplies')

urlpatterns = [
    path('', include(router.urls)),
]