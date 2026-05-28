# apps/stock/services_orders.py
import datetime
from decimal import Decimal
from django.db import transaction

from apps.stock.models import PurchaseOrder, PurchaseOrderItem, SupplyBatch


class PurchaseOrderService:
    @staticmethod
    @transaction.atomic
    def approve_order(order: PurchaseOrder, manager=None) -> PurchaseOrder:
        if order.status != 'REQUESTED':
            raise ValueError(
                f"Solo se pueden aprobar órdenes en estado REQUESTED. "
                f"Estado actual: {order.status}"
            )

        order.status = 'APPROVED'
        if manager:
            order.manager = manager
        order.save(update_fields=['status', 'manager', 'updated_at'])
        return order

    @staticmethod
    @transaction.atomic
    def receive_order(
        order: PurchaseOrder,
        received_items: list[dict]
    ) -> tuple[PurchaseOrder, list[SupplyBatch]]:
        if order.status != 'APPROVED':
            raise ValueError(
                f"Solo se pueden recibir órdenes en estado APPROVED. "
                f"Estado actual: {order.status}"
            )

        created_batches = []

        for item_data in received_items:
            order_item = PurchaseOrderItem.objects.select_related(
                'supply'
            ).get(
                pk=item_data['item_id'],
                order=order
            )

            batch = SupplyBatch.objects.create(
                supply=order_item.supply,
                lot_number=item_data['lot_number'],
                expiration_date=item_data['expiration_date'],
                initial_stock=item_data['quantity_received'],
                current_stock=item_data['quantity_received'],
                acquisition_cost=order_item.unit_cost,
            )
            created_batches.append(batch)

        order.status = 'RECEIVED'
        order.save(update_fields=['status', 'updated_at'])

        return order, created_batches

    @staticmethod
    @transaction.atomic
    def cancel_order(
        order: PurchaseOrder,
        reason: str = ''
    ) -> PurchaseOrder:
        if order.status in ('RECEIVED', 'CANCELLED'):
            raise ValueError(
                f"No se puede cancelar una orden en estado {order.status}."
            )

        order.status = 'CANCELLED'
        order.save(update_fields=['status', 'updated_at'])
        return order