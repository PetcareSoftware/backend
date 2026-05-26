# apps/stock/tests/test_orders.py
import uuid
from decimal import Decimal
from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient

from apps.stock.models import (
    Supplier, Supply, SupplyBatch,
    PurchaseOrder, PurchaseOrderItem,
)
from apps.stock.services_orders import PurchaseOrderService


class PurchaseOrderServiceTest(TestCase):
    """Tests para la lógica de negocio del servicio de órdenes."""

    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="TestSupplier",
            phone="123",
            email="test@sup.com",
            address="Addr"
        )
        self.supply = Supply.objects.create(
            sku="MED-001",
            name="Amoxicilina",
            category="MEDICINE",
            min_stock_alert=10
        )

    def _create_order_with_items(self):
        """Helper: crea una orden con un ítem."""
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            total_cost=Decimal("625.00"),
            status='REQUESTED'
        )
        item = PurchaseOrderItem.objects.create(
            order=order,
            supply=self.supply,
            quantity_requested=50,
            unit_cost=Decimal("12.50")
        )
        return order, item

    def test_approve_order(self):
        order, _ = self._create_order_with_items()
        service = PurchaseOrderService()
        result = service.approve_order(order)
        self.assertEqual(result.status, 'APPROVED')

    def test_approve_non_requested_order_fails(self):
        order, _ = self._create_order_with_items()
        order.status = 'APPROVED'
        order.save()
        service = PurchaseOrderService()
        with self.assertRaises(ValueError):
            service.approve_order(order)

    def test_receive_order_creates_batches(self):
        order, item = self._create_order_with_items()
        order.status = 'APPROVED'
        order.save()

        service = PurchaseOrderService()
        updated_order, batches = service.receive_order(
            order=order,
            received_items=[{
                'item_id': item.id,
                'lot_number': 'LOT-2025-A',
                'expiration_date': date(2026, 6, 30),
                'quantity_received': 50,
            }]
        )

        self.assertEqual(updated_order.status, 'RECEIVED')
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0].current_stock, 50)
        self.assertEqual(batches[0].lot_number, 'LOT-2025-A')
        self.assertEqual(batches[0].supply, self.supply)

    def test_receive_non_approved_order_fails(self):
        order, item = self._create_order_with_items()
        # Orden aún en REQUESTED
        service = PurchaseOrderService()
        with self.assertRaises(ValueError):
            service.receive_order(
                order=order,
                received_items=[{
                    'item_id': item.id,
                    'lot_number': 'LOT-X',
                    'expiration_date': date(2026, 12, 31),
                    'quantity_received': 50,
                }]
            )

    def test_cancel_requested_order(self):
        order, _ = self._create_order_with_items()
        service = PurchaseOrderService()
        result = service.cancel_order(order)
        self.assertEqual(result.status, 'CANCELLED')

    def test_cancel_approved_order(self):
        order, _ = self._create_order_with_items()
        order.status = 'APPROVED'
        order.save()
        service = PurchaseOrderService()
        result = service.cancel_order(order)
        self.assertEqual(result.status, 'CANCELLED')

    def test_cancel_received_order_fails(self):
        order, _ = self._create_order_with_items()
        order.status = 'RECEIVED'
        order.save()
        service = PurchaseOrderService()
        with self.assertRaises(ValueError):
            service.cancel_order(order)


class PurchaseOrderAPITest(TestCase):
    """Tests para los endpoints de la API de órdenes."""

    def setUp(self):
        self.client = APIClient()
        self.supplier = Supplier.objects.create(
            name="APISupplier",
            phone="789",
            email="api@sup.com",
            address="API Addr"
        )
        self.supply = Supply.objects.create(
            sku="CON-001",
            name="Guantes",
            category="CONSUMABLE",
            min_stock_alert=50
        )

    def test_create_order_from_interface_vue_payload(self):
        """Test con el payload exacto que envía Interface.vue."""
        payload = {
            'proveedor': str(self.supplier.id),
            'items': [
                {
                    'insumoId': str(self.supply.id),
                    'nombre': 'Guantes',
                    'cantidad': 200,
                    'costoUnitario': '0.50'
                }
            ]
        }
        resp = self.client.post(
            '/api/stock/orders/',
            payload,
            format='json'
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['status'], 'REQUESTED')
        self.assertEqual(resp.data['total_cost'], '100.00')
        self.assertEqual(len(resp.data['items']), 1)

    def test_create_order_invalid_supplier(self):
        payload = {
            'proveedor': str(uuid.uuid4()),  # UUID inexistente
            'items': [{
                'insumoId': str(self.supply.id),
                'cantidad': 10,
                'costoUnitario': '5.00'
            }]
        }
        resp = self.client.post(
            '/api/stock/orders/',
            payload,
            format='json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_create_order_empty_items(self):
        payload = {
            'proveedor': str(self.supplier.id),
            'items': []
        }
        resp = self.client.post(
            '/api/stock/orders/',
            payload,
            format='json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_full_workflow(self):
        """Test del flujo completo: crear → aprobar → recibir."""
        # 1. Crear
        create_resp = self.client.post('/api/stock/orders/', {
            'proveedor': str(self.supplier.id),
            'items': [{
                'insumoId': str(self.supply.id),
                'cantidad': 100,
                'costoUnitario': '2.50'
            }]
        }, format='json')
        order_id = create_resp.data['id']
        item_id = create_resp.data['items'][0]['id']

        # 2. Aprobar
        approve_resp = self.client.post(
            f'/api/stock/orders/{order_id}/approve/'
        )
        self.assertEqual(approve_resp.data['status'], 'APPROVED')

        # 3. Recibir
        receive_resp = self.client.post(
            f'/api/stock/orders/{order_id}/receive/',
            {
                'received_items': [{
                    'item_id': item_id,
                    'lot_number': 'LOT-FULL-TEST',
                    'expiration_date': '2026-12-31',
                    'quantity_received': 100
                }]
            },
            format='json'
        )
        self.assertEqual(receive_resp.data['status'], 'RECEIVED')
        self.assertEqual(receive_resp.data['batches_created'], 1)

        # Verificar que se creó el lote
        self.assertEqual(
            SupplyBatch.objects.filter(
                lot_number='LOT-FULL-TEST'
            ).count(), 1
        )

    def test_cancel_order(self):
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            total_cost=Decimal("100.00"),
            status='REQUESTED'
        )
        resp = self.client.post(
            f'/api/stock/orders/{order.id}/cancel/',
            {'reason': 'Test cancelación'},
            format='json'
        )
        self.assertEqual(resp.data['status'], 'CANCELLED')

    def test_filter_by_status(self):
        PurchaseOrder.objects.create(
            supplier=self.supplier, total_cost=100, status='REQUESTED'
        )
        PurchaseOrder.objects.create(
            supplier=self.supplier, total_cost=200, status='APPROVED'
        )
        resp = self.client.get(
            '/api/stock/orders/by-status/?status=REQUESTED'
        )
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['status'], 'REQUESTED')