import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.stock.models import Supply, SupplyBatch, Supplier
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class SupplyAPITestCase(TestCase):
    """Pruebas para el endpoint /api/v1/inventory/supplies/"""

    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            email='test@petcare.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Crear insumo de prueba
        self.supply = Supply.objects.create(
            sku='SKU-TEST-001',
            name='Jeringa 5ml',
            description='Jeringa descartable',
            category='CONSUMABLE',
            min_stock_alert=10
        )

        # Crear lotes de prueba
        self.batch1 = SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-A01',
            expiration_date=timezone.now().date() + datetime.timedelta(days=180),
            initial_stock=100,
            current_stock=80,
            acquisition_cost=Decimal('0.50')
        )
        self.batch2 = SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-A02',
            expiration_date=timezone.now().date() + datetime.timedelta(days=365),
            initial_stock=50,
            current_stock=50,
            acquisition_cost=Decimal('0.55')
        )

    def test_list_supplies(self):
        """Verificar que GET /supplies/ retorna la lista de insumos"""
        response = self.client.get('/api/v1/inventory/supplies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_supply_has_calculated_quantity(self):
        """Verificar que quantity = suma de current_stock de lotes activos"""
        response = self.client.get('/api/v1/inventory/supplies/')
        supply_data = response.data[0]
        self.assertEqual(supply_data['quantity'], 130)

    def test_supply_has_unit_cost(self):
        """Verificar que unitCost = costo del último lote creado"""
        response = self.client.get('/api/v1/inventory/supplies/')
        supply_data = response.data[0]
        self.assertEqual(supply_data['unitCost'], 0.55)

    def test_supply_has_umbral(self):
        """Verificar que umbral mapea a min_stock_alert"""
        response = self.client.get('/api/v1/inventory/supplies/')
        supply_data = response.data[0]
        self.assertEqual(supply_data['umbral'], 10)

    def test_supply_has_active_batches(self):
        """Verificar que batches contiene solo lotes activos"""
        response = self.client.get('/api/v1/inventory/supplies/')
        supply_data = response.data[0]
        self.assertEqual(len(supply_data['batches']), 2)
        batch = supply_data['batches'][0]
        self.assertIn('batch', batch) 
        self.assertIn('expirationDate', batch) 
        self.assertIn('quantity', batch) 

    def test_create_supply(self):
        """Verificar que POST /supplies/ crea un insumo"""
        data = {
            'sku': 'SKU-NEW-001',
            'name': 'Gasa estéril',
            'category': 'CONSUMABLE',
            'min_stock_alert': 20
        }
        response = self.client.post(
            '/api/v1/inventory/supplies/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supply.objects.count(), 2)

    def test_expired_batches_excluded_from_quantity(self):
        """Verificar que lotes vencidos no se suman al quantity"""
        SupplyBatch.objects.create(
            supply=self.supply,
            lot_number='LOT-EXPIRED',
            expiration_date=timezone.now().date() - datetime.timedelta(days=1),
            initial_stock=200,
            current_stock=200,
            acquisition_cost=Decimal('1.00')
        )
        response = self.client.get('/api/v1/inventory/supplies/')
        supply_data = response.data[0]
        self.assertEqual(supply_data['quantity'], 130)

    def test_unauthenticated_request_rejected(self):
        """Verificar que peticiones sin autenticación son rechazadas"""
        client = APIClient() 
        response = client.get('/api/v1/inventory/supplies/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SupplierAPITestCase(TestCase):
    """Pruebas para el endpoint /api/v1/inventory/suppliers/"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test2@petcare.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_supplier(self):
        """Verificar que POST /suppliers/ crea un proveedor"""
        data = {
            'name': 'Proveedor Veterinario SA',
            'phone': '555-1234',
            'email': 'proveedor@vet.com',
            'address': 'Calle Principal 100'
        }
        response = self.client.post(
            '/api/v1/inventory/suppliers/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 1)

    def test_list_suppliers(self):
        """Verificar que GET /suppliers/ retorna la lista de proveedores"""
        Supplier.objects.create(
            name='Test Supplier',
            phone='555-0000',
            email='test@sup.com',
            address='Dirección test'
        )
        response = self.client.get('/api/v1/inventory/suppliers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)