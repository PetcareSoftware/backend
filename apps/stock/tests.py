import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status as http_status
from apps.stock.models import (
    Supply, SupplyBatch, ConsultationSupply
)
from apps.stock.services import consume_supply_fifo
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class ConsumeFIFOServiceTestCase(TestCase):
    """Pruebas unitarias del servicio consume_supply_fifo."""

    def setUp(self):
        self.supply = Supply.objects.create(
            sku='SKU-FIFO-01',
            name='Test FIFO Supply',
            category='MEDICINE',
            min_stock_alert=5
        )
        # Lote A: vence primero (debe consumirse primero)
        self.batch_a = SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-A',
            expiration_date=timezone.now().date() + datetime.timedelta(days=30),
            initial_stock=10,
            current_stock=10,
            acquisition_cost=Decimal('5.00')
        )
        # Lote B: vence después
        self.batch_b = SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-B',
            expiration_date=timezone.now().date() + datetime.timedelta(days=180),
            initial_stock=25,
            current_stock=25,
            acquisition_cost=Decimal('5.50')
        )
        # Lote C: vence más tarde
        self.batch_c = SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-C',
            expiration_date=timezone.now().date() + datetime.timedelta(days=365),
            initial_stock=50,
            current_stock=50,
            acquisition_cost=Decimal('6.00')
        )

    def test_consume_from_first_batch(self):
        consume_supply_fifo(self.supply.id, 5)
        self.batch_a.refresh_from_db()
        self.assertEqual(self.batch_a.current_stock, 5)
        self.batch_b.refresh_from_db()
        self.assertEqual(self.batch_b.current_stock, 25)

    def test_consume_spanning_two_batches(self):
        consume_supply_fifo(self.supply.id, 15)
        self.batch_a.refresh_from_db()
        self.assertEqual(self.batch_a.current_stock, 0)
        self.batch_b.refresh_from_db()
        self.assertEqual(self.batch_b.current_stock, 20)

    def test_consume_spanning_three_batches(self):
        consume_supply_fifo(self.supply.id, 40)
        self.batch_a.refresh_from_db()
        self.assertEqual(self.batch_a.current_stock, 0)
        self.batch_b.refresh_from_db()
        self.assertEqual(self.batch_b.current_stock, 0)
        self.batch_c.refresh_from_db()
        self.assertEqual(self.batch_c.current_stock, 45)

    def test_consume_exact_total(self):
        consume_supply_fifo(self.supply.id, 85)
        self.batch_a.refresh_from_db()
        self.assertEqual(self.batch_a.current_stock, 0)
        self.batch_b.refresh_from_db()
        self.assertEqual(self.batch_b.current_stock, 0)
        self.batch_c.refresh_from_db()
        self.assertEqual(self.batch_c.current_stock, 0)

    def test_consume_exceeds_stock_raises_error(self):
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            consume_supply_fifo(self.supply.id, 100)

    def test_consume_zero_raises_error(self):
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            consume_supply_fifo(self.supply.id, 0)

    def test_consume_negative_raises_error(self):
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            consume_supply_fifo(self.supply.id, -5)

    def test_nonexistent_supply_raises_error(self):
        from rest_framework.exceptions import ValidationError
        fake_id = uuid.uuid4()
        with self.assertRaises(ValidationError):
            consume_supply_fifo(fake_id, 5)

    def test_expired_batches_excluded(self):
        SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-EXPIRED',
            expiration_date=timezone.now().date() - datetime.timedelta(days=1),
            initial_stock=1000,
            current_stock=1000,
            acquisition_cost=Decimal('1.00')
        )
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            consume_supply_fifo(self.supply.id, 100)

    def test_consultation_supply_created(self):
        consultation_id = uuid.uuid4()
        consume_supply_fifo(self.supply.id, 15, consultation_id=consultation_id)
        records = ConsultationSupply.objects.filter(consultation_id=consultation_id)
        self.assertEqual(records.count(), 2)
        total_consumed = sum(r.quantity_used for r in records)
        self.assertEqual(total_consumed, 15)

    def test_no_consultation_supply_without_id(self):
        consume_supply_fifo(self.supply.id, 5)
        self.assertEqual(ConsultationSupply.objects.count(), 0)


class ConsumeEndpointTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='miguel@petcare.com',
            password='testpass123',
            first_name='Miguel', last_name='Dev'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.supply = Supply.objects.create(
            sku='SKU-EP-01', name='Gasa Test',
            category='CONSUMABLE', min_stock_alert=5
        )
        SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-EP-A',
            expiration_date=timezone.now().date() + datetime.timedelta(days=90),
            initial_stock=50, current_stock=50,
            acquisition_cost=Decimal('1.00')
        )

    def test_consume_success(self):
        data = {"supply_id": str(self.supply.id), "quantity": 10}
        response = self.client.post('/api/v1/inventory/consume/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['remaining_stock'], 40)

    def test_consume_with_consultation(self):
        consult_id = str(uuid.uuid4())
        data = {"supply_id": str(self.supply.id), "quantity": 5, "consultation_id": consult_id}
        response = self.client.post('/api/v1/inventory/consume/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConsultationSupply.objects.count(), 1)

    def test_consume_insufficient_stock(self):
        data = {"supply_id": str(self.supply.id), "quantity": 999}
        response = self.client.post('/api/v1/inventory/consume/', data, format='json')
        self.assertEqual(response.status_code, 422)

    def test_consume_missing_fields(self):
        response = self.client.post('/api/v1/inventory/consume/', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_rejected(self):
        client = APIClient()
        data = {"supply_id": str(self.supply.id), "quantity": 1}
        response = client.post('/api/v1/inventory/consume/', data, format='json')
        self.assertEqual(response.status_code, 401)
