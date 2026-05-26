from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.stock.views import SupplyViewSet, SupplierViewSet

router = DefaultRouter()
router.register(r'supplies', SupplyViewSet, basename='supplies')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')

urlpatterns = [
    path('', include(router.urls)),
]