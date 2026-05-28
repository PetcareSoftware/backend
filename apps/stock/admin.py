# apps/stock/admin.py
from django.contrib import admin
from .models import Supplier, Supply, SupplyBatch, ConsultationSupply, PurchaseOrder, PurchaseOrderItem
from .models import ClinicalProcedureSupply

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'phone', 'email')
    search_fields = ('name', 'email')

@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'min_stock')
    list_filter = ('category',)
    search_fields = ('sku', 'name')

@admin.register(SupplyBatch)
class SupplyBatchAdmin(admin.ModelAdmin):
    list_display = ('supply', 'lot_number', 'expiration_date', 'current_stock')
    list_filter = ('expiration_date',)
    search_fields = ('lot_number',)

@admin.register(ConsultationSupply)
class ConsultationSupplyAdmin(admin.ModelAdmin):
    list_display = ('consultation_id', 'batch', 'quantity_used')
    search_fields = ('consultation_id',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'total_cost', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('supplier__name',)

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'supply', 'quantity_requested', 'unit_cost')
    search_fields = ('order__id', 'supply__name')

@admin.register(ClinicalProcedureSupply)
class ClinicalProcedureSupplyAdmin(admin.ModelAdmin):
    list_display = ('procedure_id', 'batch', 'quantity_used')
    search_fields = ('procedure_id', 'batch__supply__name')  # opcional