import datetime
import uuid
import logging
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.stock.models import Supply, Supplier, SupplyBatch
from apps.stock.serializers import (
    SupplySerializer,
    SupplyWriteSerializer,
    SupplierSerializer,
    BatchCreateFromFrontendSerializer,
    BatchReadSerializer,
)
from apps.stock.services import consume_supply_fifo

logger = logging.getLogger(__name__)


class SupplyViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD completo para el catálogo maestro de insumos.
    """
    queryset = Supply.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Utiliza el serializador de lectura (con campos calculados)
        para GET y el de escritura (campos nativos) para POST/PUT/PATCH.
        """
        if self.action in ['list', 'retrieve']:
            return SupplySerializer
        return SupplyWriteSerializer

    def create(self, request, *args, **kwargs):
        """
        Permite registrar un insumo mapeando los datos en español provenientes de form.vue:
        - nombre/name → name
        - tipo/category → category (mapeado de "Medicamento"/"Insumo" a MEDICINE/CONSUMABLE)
        - cantidad/quantity → Crea un lote de inventario inicial
        - precio/unitCost → Costo de adquisición por unidad del lote inicial
        - umbral/umbral → min_stock_alert
        """
        data = request.data
        name = data.get('nombre') or data.get('name')
        if not name:
            return Response({"error": "El nombre del insumo es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        category_raw = data.get('tipo') or data.get('category')

        # Mapeo de categorías español -> inglés
        category = 'CONSUMABLE'
        if category_raw:
            cat_lower = category_raw.lower()
            if 'med' in cat_lower:
                category = 'MEDICINE'
            elif 'vac' in cat_lower:
                category = 'VACCINE'
            elif 'equ' in cat_lower:
                category = 'EQUIPMENT'

        min_stock_alert = data.get('umbral') or data.get('min_stock_alert') or 10
        sku = data.get('sku') or f"SKU-{uuid.uuid4().hex[:8].upper()}"
        description = data.get('observaciones') or data.get('description') or ""

        # Crear el insumo maestro
        supply = Supply.objects.create(
            sku=sku,
            name=name,
            description=description,
            category=category,
            min_stock_alert=int(min_stock_alert)
        )

        # Crear lote inicial de forma automática si se provee cantidad y precio
        initial_qty = data.get('cantidad') or data.get('quantity')
        price = data.get('precio') or data.get('unitCost')

        if initial_qty is not None and price is not None:
            # Limpiar valor numérico del precio si viene con signo de dólar
            price_clean = str(price).replace('$', '').strip()
            SupplyBatch.objects.create(
                supply=supply,
                lot_number=data.get('lote') or 'LOT-INITIAL',
                expiration_date=data.get('expiration_date') or (timezone.now() + datetime.timedelta(days=365)).date(),
                initial_stock=int(initial_qty),
                current_stock=int(initial_qty),
                acquisition_cost=Decimal(price_clean)
            )

        serializer = self.get_serializer(supply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Lista todos los insumos con sus campos calculados.
        El frontend (InventoryCatalog.vue) consume este endpoint
        para mostrar la tabla de inventario.
        """
        queryset = self.get_queryset().prefetch_related('batches')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Detalle de un insumo individual con todos sus lotes activos.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD completo para proveedores.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]


class InventoryConsumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        supply_id = request.data.get('supply_id')
        quantity = request.data.get('quantity')
        consultation_id = request.data.get('consultation_id')
        procedure_id = request.data.get('procedure_id')

        if not supply_id or not quantity:
            return Response(
                {"error": "Los campos 'supply_id' y 'quantity' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response(
                {"error": "La cantidad debe ser un número entero válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_supply = consume_supply_fifo(
                supply_id, quantity,
                consultation_id=consultation_id,
                procedure_id=procedure_id
            )
            return Response({
                "message": "Consumo FIFO registrado con éxito.",
                "supply_id": updated_supply.id,
                "name": updated_supply.name
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


# --- Views de Pascia (origin/b2/feature/gestion-lotes-alertas) ---

class SupplyBatchCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BatchCreateFromFrontendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        supply = Supply.objects.get(id=validated['insumoId'])

        acquisition_cost = validated.get('acquisitionCost')
        if not acquisition_cost:
            latest_batch = supply.batches.order_by('-created_at').first()
            acquisition_cost = latest_batch.acquisition_cost if latest_batch else Decimal('0.00')

        batch = SupplyBatch.objects.create(
            supply=supply,
            lot_number=validated['batch'],
            expiration_date=validated['expirationDate'],
            initial_stock=validated['quantity'],
            current_stock=validated['quantity'],
            acquisition_cost=acquisition_cost
        )

        read_serializer = BatchReadSerializer(batch)
        return Response({"message": "Lote registrado exitosamente.", "batch": read_serializer.data}, status=status.HTTP_201_CREATED)

    def get(self, request):
        today = timezone.now().date()
        queryset = SupplyBatch.objects.filter(
            expiration_date__gt=today,
            current_stock__gt=0
        ).select_related('supply').order_by('expiration_date')

        serializer = BatchReadSerializer(queryset, many=True)
        return Response(serializer.data)


class InventoryAlertsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        alerts = []

        for supply in Supply.objects.all():
            active_stock = supply.batches.filter(expiration_date__gt=today, current_stock__gt=0).aggregate(total=Sum('current_stock'))['total'] or 0
            min_alert = supply.min_stock_alert
            warning_threshold = int(min_alert * 1.5)

            if active_stock <= min_alert:
                alerts.append({
                    "supply_id": supply.id,
                    "supply_name": supply.name,
                    "supply_sku": supply.sku,
                    "alert_type": "LOW_STOCK",
                    "severity": "critical",
                    "message": f"CRÍTICO: '{supply.name}' tiene {active_stock} uds.",
                    "current_value": active_stock,
                    "threshold_value": min_alert
                })
            elif active_stock <= warning_threshold:
                alerts.append({
                    "supply_id": supply.id,
                    "supply_name": supply.name,
                    "supply_sku": supply.sku,
                    "alert_type": "LOW_STOCK",
                    "severity": "warning",
                    "message": f"ALERTA: '{supply.name}' tiene {active_stock} uds.",
                    "current_value": active_stock,
                    "threshold_value": min_alert
                })

        limit_date = today + datetime.timedelta(days=45)
        expiring_batches = SupplyBatch.objects.filter(expiration_date__gt=timezone.now().date(), expiration_date__lte=limit_date, current_stock__gt=0).select_related('supply')

        for batch in expiring_batches:
            days_remaining = (batch.expiration_date - today).days
            severity = 'critical' if days_remaining <= 15 else 'warning'

            alerts.append({
                "supply_id": batch.supply.id,
                "supply_name": batch.supply.name,
                "supply_sku": batch.supply.sku,
                "alert_type": "NEAR_EXPIRATION",
                "severity": severity,
                "message": f"Lote '{batch.lot_number}' vence en {days_remaining} días.",
                "current_value": batch.current_stock,
                "days_remaining": days_remaining,
                "batch_id": batch.id,
                "lot_number": batch.lot_number
            })

        alerts.sort(key=lambda a: 0 if a['severity'] == 'critical' else 1)
        return Response({"alerts": alerts})
