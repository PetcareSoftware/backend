from django.urls import path
from apps.stock.views import SupplyBatchCreateView, InventoryAlertsView

urlpatterns = [
    path('batches/', SupplyBatchCreateView.as_view(), name='inventory-batches'),
    path('alerts/', InventoryAlertsView.as_view(), name='inventory-alerts'),
]