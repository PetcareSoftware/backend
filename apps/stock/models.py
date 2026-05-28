from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group

class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    address = models.TextField()

    class Meta:
        db_table = 'suppliers'

    def __str__(self):
        return self.name

class Supply(models.Model):
    CATEGORY_CHOICES = [
        ('MEDICINE', 'Medicamento'),
        ('VACCINE', 'Vacuna'),
        ('CONSUMABLE', 'Consumible'),
        ('EQUIPMENT', 'Equipo'),
    ]
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    min_stock = models.IntegerField(default=0)   # antes min_stock_alert

    class Meta:
        db_table = 'supplies'

    def __str__(self):
        return f"{self.sku} - {self.name}"

class SupplyBatch(models.Model):
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, related_name='batches')
    lot_number = models.CharField(max_length=50)
    expiration_date = models.DateField()
    initial_stock = models.IntegerField()
    current_stock = models.IntegerField()
    acquisition_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supply_batches'

    def __str__(self):
        return f"{self.supply.name} - Lote {self.lot_number}"

class ConsultationSupply(models.Model):
    consultation_id = models.BigIntegerField(help_text="ID de la consulta (tabla consultations)")
    batch = models.ForeignKey(SupplyBatch, on_delete=models.CASCADE, related_name='consultation_usages')
    quantity_used = models.IntegerField()

    class Meta:
        db_table = 'consultation_supplies'
        unique_together = (('consultation_id', 'batch'),)

    def __str__(self):
        return f"Uso en consulta {self.consultation_id} - {self.batch.supply.name} x{self.quantity_used}"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Solicitada'),
        ('APPROVED', 'Aprobada'),
        ('RECEIVED', 'Recibida'),
        ('CANCELLED', 'Cancelada'),
    ]
    # Este se mantiene intacto: Django sabe que AUTH_USER_MODEL usa UUID y lo enlaza correctamente
    manager = models.ForeignKey(Group,on_delete=models.SET_NULL, null=True,blank=True,related_name='purchase_orders')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_orders'

    def __str__(self):
        return f"Orden {self.id} - {self.supplier.name}"

class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, related_name='purchase_items')
    quantity_requested = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'purchase_order_items'

    def __str__(self):
        return f"{self.supply.name} - {self.quantity_requested} unidades"
    
class ClinicalProcedureSupply(models.Model):
    # Adaptado a bigint para coincidir con la tabla clinical_procedures
    procedure_id = models.BigIntegerField(help_text="ID del procedimiento clínico")
    batch = models.ForeignKey(SupplyBatch, on_delete=models.CASCADE, related_name='procedure_usages')
    quantity_used = models.IntegerField()

    class Meta:
        db_table = 'clinical_procedures_supplies'
        unique_together = (('procedure_id', 'batch'),)
        verbose_name = 'Insumo utilizado en procedimiento'
        verbose_name_plural = 'Insumos utilizados en procedimientos'

    def __str__(self):
        return f"Proc {self.procedure_id} - {self.batch.supply.name} x{self.quantity_used}"

class AuditSupplyBatch(models.Model):
    audit_id = models.BigAutoField(primary_key=True)
    batch_id = models.BigIntegerField() 
    action = models.CharField(max_length=10)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    changed_at = models.DateTimeField()
    changed_by = models.CharField(max_length=255)

    class Meta:
        managed = False 
        db_table = 'audit_supply_batches'
        verbose_name = 'Auditoría de Lote'
        verbose_name_plural = 'Auditorías de Lotes'

    def __str__(self):
        return f"{self.action} en Lote {self.batch_id} - {self.changed_at.strftime('%Y-%m-%d %H:%M')}"
