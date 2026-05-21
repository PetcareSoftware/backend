from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class MedicalSupply(models.Model):
    """
    Catálogo maestro centralizado de insumos, consumibles y medicamentos.
    Soporta el caso de uso CU-14.
    """
    id_supply = models.AutoField(primary_key=True)
    supply_name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre comercial del insumo"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción o detalles técnicos"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Costo unitario base de referencia en USD"
    )
    minimum_stock = models.PositiveIntegerField(
        verbose_name="Umbral mínimo de seguridad"
    )
    current_stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Existencias globales reales acumuladas"
    )

    @property
    def needs_replenishment(self):
        """
        Determina si las existencias actuales están por debajo del umbral configurado.
        """
        return self.current_stock <= self.minimum_stock

    def __str__(self):
        return self.supply_name


class SupplyBatch(models.Model):
    """
    Gestiona el fraccionamiento físico de existencias por lotes.
    Soporta los escenarios CU-15 y CU-16 (caducidades y orden de consumo FIFO).
    """
    id_batch = models.AutoField(primary_key=True)
    id_supply = models.ForeignKey(
        MedicalSupply,
        on_delete=models.CASCADE,
        related_name="batches",
        verbose_name="Insumo médico de referencia"
    )
    batch_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código único de lote provisto por laboratorio"
    )
    quantity_received = models.PositiveIntegerField(
        verbose_name="Cantidad inicial ingresada"
    )
    quantity_available = models.PositiveIntegerField(
        verbose_name="Unidades remanentes reales no consumidas"
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora de registro del ingreso"
    )
    expiration_date = models.DateField(
        verbose_name="Fecha de caducidad estipulada por fabricante"
    )

    def __str__(self):
        return f"Lote {self.batch_code} - {self.id_supply.supply_name}"


class PurchaseRequest(models.Model):
    """
    Cabecera del flujo transaccional de reabastecimiento financiero.
    Soporta los escenarios CU-18 y CU-19.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente de Revisión'),
        ('APPROVED', 'Aprobada por Gerencia'),
        ('REJECTED', 'Rechazada por Gerencia'),
    ]

    id_purchase_request = models.AutoField(primary_key=True)
    id_applicant_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="submitted_requests",
        verbose_name="Técnico Veterinario solicitante"
    )
    id_approver_manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="resolved_requests",
        verbose_name="Gerente que resolvió la orden"
    )
    request_status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Estado actual del workflow"
    )
    request_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación de la solicitud"
    )
    resolution_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha en que se aprobó/rechazó"
    )
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Justificación obligatoria en caso de rechazo"
    )

    def __str__(self):
        return f"Solicitud #{self.id_purchase_request} - {self.request_status}"


class PurchaseRequestDetail(models.Model):
    """
    Desglose detallado de ítems dentro de una solicitud de compra.
    """
    id_detail = models.AutoField(primary_key=True)
    id_purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name="Solicitud cabecera"
    )
    id_supply = models.ForeignKey(
        MedicalSupply,
        on_delete=models.PROTECT,
        verbose_name="Insumo médico requerido"
    )
    quantity_requested = models.PositiveIntegerField(
        verbose_name="Cantidad solicitada (mínimo 1)"
    )
    estimated_unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Costo congelado al momento del pedido"
    )

    def __str__(self):
        return f"Detalle {self.id_detail} - Req #{self.id_purchase_request.id_purchase_request}"


class StockAlertLog(models.Model):
    """
    Registro histórico de desviaciones operativas y de caducidades.
    Soporta el escenario CU-16.
    """
    ALERT_TYPES = [
        ('MINIMUM_STOCK', 'Stock por debajo del mínimo'),
        ('NEAR_EXPIRATION', 'Lote cercano a vencer o caducado'),
    ]

    id_alert = models.AutoField(primary_key=True)
    id_supply = models.ForeignKey(
        MedicalSupply,
        on_delete=models.CASCADE,
        verbose_name="Insumo afectado"
    )
    id_batch = models.ForeignKey(
        SupplyBatch,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Lote afectado (opcional)"
    )
    alert_type = models.CharField(
        max_length=25,
        choices=ALERT_TYPES,
        verbose_name="Naturaleza de la desviación"
    )
    notification_detail = models.TextField(
        verbose_name="Texto redactado con el detalle del evento"
    )
    alert_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora de generación de la alerta"
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name="Flag de subsanado"
    )

    def __str__(self):
        return f"Alerta {self.alert_type} - {self.id_supply.supply_name}"