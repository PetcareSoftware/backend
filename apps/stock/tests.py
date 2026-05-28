import uuid
from decimal import Decimal
from datetime import date
from django.test import TestCase
from apps.stock.models import (
    Supplier, Supply, SupplyBatch,
    ConsultationSupply, PurchaseOrder,
    PurchaseOrderItem, ClinicalProcedureSupply,
)


class SupplierModelTest(TestCase):
    def test_create_supplier(self):
        supplier = Supplier.objects.create(
            name="PetMed Supplies",
            contact_name="Juan Pérez",
            phone="+58 412 1234567",
            email="ventas@petmed.com",
            address="Av. Principal #123, Caracas"
        )
        self.assertIsInstance(supplier.id, int)
        self.assertEqual(str(supplier), "PetMed Supplies")

    def test_supplier_unique_name(self):
        Supplier.objects.create(
            name="UniqueSupplier",
            phone="123", email="a@b.com", address="addr"
        )
        with self.assertRaises(Exception):
            Supplier.objects.create(
                name="UniqueSupplier",
                phone="456", email="c@d.com", address="addr2"
            )


class SupplyModelTest(TestCase):
    def test_create_supply(self):
        supply = Supply.objects.create(
            sku="MED-001",
            name="Amoxicilina 500mg",
            description="Antibiótico de amplio espectro",
            category="MEDICINE",
            min_stock_alert=10
        )
        self.assertIsInstance(supply.id, int)
        self.assertEqual(str(supply), "MED-001 - Amoxicilina 500mg")
        self.assertEqual(supply.category, "MEDICINE")

    def test_category_choices(self):
        valid_categories = ['MEDICINE', 'VACCINE', 'CONSUMABLE', 'EQUIPMENT']
        for cat in valid_categories:
            supply = Supply(
                sku=f"TST-{cat[:3]}",
                name=f"Test {cat}",
                category=cat,
                min_stock_alert=5
            )
            supply.full_clean()  # No debe lanzar excepción


class SupplyBatchModelTest(TestCase):
    def setUp(self):
        self.supply = Supply.objects.create(
            sku="VAC-001",
            name="Vacuna Rabia",
            category="VACCINE",
            min_stock_alert=20
        )

    def test_create_batch(self):
        batch = SupplyBatch.objects.create(
            supply=self.supply,
            lot_number="LOT-2025-A",
            expiration_date=date(2026, 6, 30),
            initial_stock=100,
            current_stock=100,
            acquisition_cost=Decimal("15.50")
        )
        self.assertIsInstance(batch.id, int)
        self.assertEqual(batch.current_stock, 100)

    def test_batch_belongs_to_supply(self):
        batch = SupplyBatch.objects.create(
            supply=self.supply,
            lot_number="LOT-2025-B",
            expiration_date=date(2026, 12, 31),
            initial_stock=50,
            current_stock=50,
            acquisition_cost=Decimal("20.00")
        )
        self.assertIn(batch, self.supply.batches.all())


class PurchaseOrderModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Proveedor Test",
            phone="123456",
            email="prov@test.com",
            address="Calle Test"
        )

    def test_create_purchase_order(self):
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            total_cost=Decimal("500.00"),
            status='REQUESTED'
        )
        self.assertIsInstance(order.id, int)
        self.assertEqual(order.status, 'REQUESTED')
        self.assertIsNone(order.manager)  # manager es nullable

    def test_add_items_to_order(self):
        supply = Supply.objects.create(
            sku="CON-001", name="Guantes Látex",
            category="CONSUMABLE", min_stock_alert=50
        )
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            total_cost=Decimal("200.00")
        )
        item = PurchaseOrderItem.objects.create(
            order=order,
            supply=supply,
            quantity_requested=100,
            unit_cost=Decimal("2.00")
        )
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(item.quantity_requested, 100)