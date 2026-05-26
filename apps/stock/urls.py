from django.urls import path
from apps.stock.views import InventoryConsumeView

urlpatterns = [
    path('consume/', InventoryConsumeView.as_view(), name='inventory-consume'),
]
