# apps/stock/tests/test_orders.py
from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model  # 👈 Importamos el modelo de usuarios
from rest_framework.test import APIClient
from apps.stock.models import Supplier, Supply, PurchaseOrder, PurchaseOrderItem
from apps.stock.services_orders import PurchaseOrderService

User = get_user_model()

class PurchaseOrderServiceTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="TestSupplier", phone="123", email="test@sup.com", address="Addr")
        self.supply = Supply.objects.create(sku="MED-001", name="Amoxicilina", category="MEDICINE", min_stock_alert=10)

    def _create_order_with_items(self):
        order = PurchaseOrder.objects.create(supplier=self.supplier, total_cost=Decimal("625.00"), status='REQUESTED')
        item = PurchaseOrderItem.objects.create(order=order, supply=self.supply, quantity_requested=50, unit_cost=Decimal("12.50"))
        return order, item

    def test_approve_order(self):
        order, _ = self._create_order_with_items()
        service = PurchaseOrderService()
        result = service.approve_order(order)
        self.assertEqual(result.status, 'APPROVED')

    def test_receive_order_creates_batches(self):
        order, item = self._create_order_with_items()
        order.status = 'APPROVED'
        order.save()
        service = PurchaseOrderService()
        updated_order, batches = service.receive_order(
            order=order, 
            received_items=[{
                'item_id': item.id, 
                'lot_number': 'LOT-2026-X', 
                'expiration_date': date(2027, 12, 31), 
                'quantity_received': 50
            }]
        )
        self.assertEqual(updated_order.status, 'RECEIVED')
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0].current_stock, 50)


class PurchaseOrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.supplier = Supplier.objects.create(name="APISupplier", phone="789", email="api@sup.com", address="API Addr")
        self.supply = Supply.objects.create(sku="CON-001", name="Guantes", category="CONSUMABLE", min_stock_alert=50)
        
        #   usuario encargado de compras para los tests
        self.user = User.objects.create_user(
            username='santiago_manager',
            email='santiago@petcare.com',
            password='Password123'
        )
        
        #  Forza la autenticación del cliente antes de cada petición de API
        self.client.force_authenticate(user=self.user)

    def test_create_order_from_payload(self):
        payload = {
            'proveedor': self.supplier.id,
            'items': [{
                'insumoId': self.supply.id, 
                'nombre': 'Guantes', 
                'cantidad': 200, 
                'costoUnitario': '0.50'
            }]
        }
        # Apunta al endpoint oficial estipulado en la arquitectura del proyecto v1
        resp = self.client.post('/api/v1/inventory/purchase-orders/', payload, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['status'], 'REQUESTED')