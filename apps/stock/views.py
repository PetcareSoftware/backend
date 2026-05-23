# apps/stock/views.py
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.stock.models import PurchaseOrder, PurchaseOrderItem, Supply, Supplier, SupplyBatch
from apps.stock.serializers import PurchaseOrderReadSerializer, PurchaseOrderCreateSerializer

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """Controlador que maneja los estados de una orden de compra de forma transaccional."""
    queryset = PurchaseOrder.objects.all().prefetch_related('items__supply')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderReadSerializer

    def create(self, request, *args, **kwargs):
        """Recibe la solicitud del Técnico Veterinario, calcula costos y la crea en estado REQUESTED."""
        serializer = PurchaseOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # Proveedor por defecto en caso de no venir en la solicitud
        supplier_id = validated.get('supplier_id')
        if supplier_id:
            try:
                supplier = Supplier.objects.get(id=supplier_id)
            except Supplier.DoesNotExist:
                return Response({"error": "El proveedor especificado no existe."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            supplier = Supplier.objects.first() or Supplier.objects.create(
                name="Proveedor General PetCare", phone="12345", email="info@petcare.com", address="San Diego"
            )

        # Bloque atómico para guardar la orden y sus líneas de ítems juntos
        with transaction.atomic():
            order = PurchaseOrder.objects.create(supplier=supplier, status='REQUESTED')
            total_cost = Decimal('0.00')

            for item_data in validated['items']:
                try:
                    insumo = Supply.objects.get(id=item_data['insumoId'])
                except Supply.DoesNotExist:
                    return Response({"error": f"Insumo {item_data['insumoId']} no encontrado."}, status=status.HTTP_400_BAD_REQUEST)

                # Obtener el costo del último lote ingresado como referencia
                ultimo_lote = insumo.batches.order_by('-created_at').first()
                costo_unitario = ultimo_lote.acquisition_cost if ultimo_lote else Decimal('1.00')

                PurchaseOrderItem.objects.create(
                    order=order, supply=insumo, quantity_requested=item_data['quantity'], unit_cost=costo_unitario
                )
                total_cost += costo_unitario * item_data['quantity']

            order.total_cost = total_cost
            order.save()

        return Response(PurchaseOrderReadSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Acción para que el Gerente apruebe la orden."""
        order = self.get_object()
        if order.status != 'REQUESTED':
            return Response({"error": "Solo se pueden aprobar órdenes en estado SOLICITADO (REQUESTED)."}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'APPROVED'
        order.save()
        return Response({"message": "Orden aprobada con éxito.", "order": PurchaseOrderReadSerializer(order).data})

    @action(detail=True, methods=['post'], url_path='receive')
    def receive(self, request, pk=None):
        """Recibe la mercancía físicamente y crea automáticamente los lotes de stock."""
        order = self.get_object()
        if order.status != 'APPROVED':
            return Response({"error": "Solo se pueden recibir órdenes que estén APROBADAS."}, status=status.HTTP_400_BAD_REQUEST)

        dias_vencimiento = int(request.data.get('expiration_days', 365))

        with transaction.atomic():
            order.status = 'RECEIVED'
            order.save()

            lotes_creados = []
            for item in order.items.all():
                # Creación automática del lote físico vinculado al insumo
                lote = SupplyBatch.objects.create(
                    supply=item.supply,
                    lot_number=f"LOTE-OC-{order.id.hex[:6].upper()}-{item.supply.sku}",
                    expiration_date=timezone.now().date() + timezone.timedelta(days=dias_vencimiento),
                    initial_stock=item.quantity_requested,
                    current_stock=item.quantity_requested,
                    acquisition_cost=item.unit_cost
                )
                lotes_creados.append({
                    "insumo": item.supply.name,
                    "numero_lote": lote.lot_number,
                    "cantidad": lote.current_stock
                })

        return Response({
            "message": "Inventario actualizado correctamente.",
            "order": PurchaseOrderReadSerializer(order).data,
            "lotes_generados": lotes_creados
        })

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancela una orden de compra activa."""
        order = self.get_object()
        if order.status not in ['REQUESTED', 'APPROVED']:
            return Response({"error": "No se puede cancelar una orden en su estado actual."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'CANCELLED'
        order.save()
        return Response({"message": "Orden cancelada correctamente.", "order": PurchaseOrderReadSerializer(order).data})