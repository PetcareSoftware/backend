# apps/stock/urls.py — VERSIÓN FINAL INTEGRADA
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# DEV2 - CRUD base
from apps.stock.views import SupplyViewSet, SupplierViewSet

# DEV3 - Órdenes de compra
from apps.stock.views_orders import PurchaseOrderViewSet

# DEV4 - Consumo FIFO
from apps.stock.views import InventoryConsumeView

# DEV5 - Lotes y Alertas
from apps.stock.views import SupplyBatchCreateView, InventoryAlertsView

router = DefaultRouter()
router.register(r'supplies', SupplyViewSet, basename='supplies')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')

urlpatterns = [
    # Router endpoints
    path('', include(router.urls)),
    # Standalone endpoints
    path('consume/', InventoryConsumeView.as_view(), name='inventory-consume'),
    path('batches/', SupplyBatchCreateView.as_view(), name='inventory-batches'),
    path('alerts/', InventoryAlertsView.as_view(), name='inventory-alerts'),
]