# apps/stock/views_orders.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from apps.stock.models import PurchaseOrder, PurchaseOrderItem
from apps.stock.serializers_orders import (
    PurchaseOrderCreateSerializer,
    PurchaseOrderReadSerializer,
    PurchaseOrderReceiveSerializer,
    PurchaseOrderCancelSerializer,
    PurchaseOrderItemReadSerializer,
)
from apps.stock.services_orders import PurchaseOrderService


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related(
        'supplier'
    ).prefetch_related(
        'items', 'items__supply'
    ).all().order_by('-created_at')
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['supplier__name', 'status']
    ordering_fields = ['created_at', 'total_cost', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        if self.action == 'receive':
            return PurchaseOrderReceiveSerializer
        if self.action == 'cancel':
            return PurchaseOrderCancelSerializer
        return PurchaseOrderReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = PurchaseOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        read_serializer = PurchaseOrderReadSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status != 'REQUESTED':
            return Response(
                {'error': 'Solo se pueden eliminar órdenes en estado REQUESTED.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        order = self.get_object()
        try:
            service = PurchaseOrderService()
            updated_order = service.approve_order(order)
            serializer = PurchaseOrderReadSerializer(updated_order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='receive')
    def receive(self, request, pk=None):
        order = self.get_object()
        serializer = PurchaseOrderReceiveSerializer(
            data=request.data,
            context={'order': order}
        )
        serializer.is_valid(raise_exception=True)

        try:
            service = PurchaseOrderService()
            updated_order, batches = service.receive_order(
                order=order,
                received_items=serializer.validated_data['received_items']
            )
            read_serializer = PurchaseOrderReadSerializer(updated_order)
            response_data = read_serializer.data
            response_data['batches_created'] = len(batches)
            return Response(response_data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()
        serializer = PurchaseOrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = PurchaseOrderService()
            updated_order = service.cancel_order(
                order=order,
                reason=serializer.validated_data.get('reason', '')
            )
            read_serializer = PurchaseOrderReadSerializer(updated_order)
            return Response(read_serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='by-status')
    def by_status(self, request):
        status_filter = request.query_params.get('status', '').upper()
        valid_statuses = [c[0] for c in PurchaseOrder.STATUS_CHOICES]

        if status_filter and status_filter not in valid_statuses:
            return Response(
                {'error': f'Estado inválido. Opciones: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = self.get_queryset()
        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = PurchaseOrderReadSerializer(qs, many=True)
        return Response(serializer.data)