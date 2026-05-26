import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status as http_status
from apps.stock.models import Supply, SupplyBatch
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()

class BatchCreationTestCase(TestCase):
    def setUp(self):
        # Creamos el usuario de prueba
        self.user = User.objects.create_user(
            email='pascia@petcare.com', 
            password='testpass123', 
            first_name='Pascia', 
            last_name='Dev'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Creamos un insumo base en la BD para poder meterle lotes
        self.supply = Supply.objects.create(
            sku='SKU-BATCH-01', 
            name='Gasa Estéril', 
            category='CONSUMABLE', 
            min_stock_alert=15
        )

    def test_create_batch_success(self):
        """Prueba que se pueda registrar un lote correctamente"""
        data = {
            "insumoId": str(self.supply.id), 
            "quantity": 50, 
            "batch": "LOT-2026-NEW", 
            "expirationDate": str(timezone.now().date() + datetime.timedelta(days=180))
        }
        response = self.client.post('/api/v1/inventory/batches/', data, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_create_batch_invalid_supply(self):
        """Prueba que falle si el insumo no existe"""
        data = {
            "insumoId": str(uuid.uuid4()), 
            "quantity": 50, 
            "batch": "LOT-INVALID", 
            "expirationDate": str(timezone.now().date() + datetime.timedelta(days=180))
        }
        response = self.client.post('/api/v1/inventory/batches/', data, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)

class AlertsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='alerts@petcare.com', 
            password='testpass123', 
            first_name='Alert', 
            last_name='Tester'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_low_stock_critical_alert(self):
        """Prueba que el endpoint de alertas detecte stock crítico"""
        supply = Supply.objects.create(
            sku='SKU-LOW', 
            name='Insumo Bajo', 
            category='MEDICINE', 
            min_stock_alert=20
        )
        # Creamos un lote con stock menor al mínimo de alerta (15 < 20)
        SupplyBatch.objects.create(
            supply=supply, 
            lot_number='LOT-LOW', 
            expiration_date=timezone.now().date() + datetime.timedelta(days=365), 
            initial_stock=15, 
            current_stock=15, 
            acquisition_cost=Decimal('5.00')
        )
        response = self.client.get('/api/v1/inventory/alerts/')
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)