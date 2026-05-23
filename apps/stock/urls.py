# apps/stock/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.stock.views import PurchaseOrderViewSet

router = DefaultRouter()
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')

urlpatterns = [
    path('', include(router.urls)),
]