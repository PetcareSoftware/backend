# apps/stock/views_orders.py
import datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.stock.models import PurchaseOrder, PurchaseOrderItem, Supply, Supplier, SupplyBatch
from apps.users.models import ClinicalStaff
from apps.stock.serializers_orders import PurchaseOrderReadSerializer, PurchaseOrderCreateSerializer

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().prefetch_related('items__supply')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = PurchaseOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        manager_id = validated.get('manager_id')
        try:
            manager_staff = ClinicalStaff.objects.get(user_id=manager_id)
        except ClinicalStaff.DoesNotExist:
            return Response({"error": "El manager no existe en el staff clínico."}, status=status.HTTP_400_BAD_REQUEST)

        supplier_id = validated.get('supplier_id')
        supplier = Supplier.objects.filter(id=supplier_id).first() if supplier_id else Supplier.objects.first()

        with transaction.atomic():
            order = PurchaseOrder.objects.create(supplier=supplier, manager=manager_staff.user, status='REQUESTED')
            total_cost = Decimal('0.00')

            for item_data in validated['items']:
                try:
                    insumo = Supply.objects.get(id=item_data['insumoId'])
                except Supply.DoesNotExist:
                    return Response({"error": f"Insumo {item_data['insumoId']} no encontrado."}, status=status.HTTP_400_BAD_REQUEST)

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
        order = self.get_object()
        if order.status != 'REQUESTED':
            return Response({"error": "Solo se pueden aprobar órdenes SOLICITADAS."}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'APPROVED'
        order.save()
        return Response({"message": "Orden aprobada.", "order": PurchaseOrderReadSerializer(order).data})

    @action(detail=True, methods=['post'], url_path='receive')
    def receive(self, request, pk=None):
        order = self.get_object()
        if order.status != 'APPROVED':
            return Response({"error": "Solo se pueden recibir órdenes APROBADAS."}, status=status.HTTP_400_BAD_REQUEST)

        dias_vencimiento = int(request.data.get('expiration_days', 365))

        with transaction.atomic():
            order.status = 'RECEIVED'
            order.save()
            lotes_creados = []
            
            for item in order.items.all():
                fecha_vencimiento = timezone.now().date() + datetime.timedelta(days=dias_vencimiento)
                
                lote = SupplyBatch.objects.create(
                    supply=item.supply,
                    lot_number=f"LOTE-OC-{order.id.hex[:6].upper()}-{item.supply.sku}",
                    expiration_date=fecha_vencimiento,
                    initial_stock=item.quantity_requested,
                    current_stock=item.quantity_requested,
                    acquisition_cost=item.unit_cost
                )
                lotes_creados.append({"insumo": item.supply.name, "cantidad": lote.current_stock})

        return Response({"message": "Inventario actualizado.", "order": PurchaseOrderReadSerializer(order).data})

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['REQUESTED', 'APPROVED']:
            return Response({"error": "No se puede cancelar en este estado."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'CANCELLED'
        order.save()
        return Response({"message": "Orden cancelada.", "order": PurchaseOrderReadSerializer(order).data})