from django.shortcuts import render
import logging
import datetime
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from apps.stock.models import Supply, SupplyBatch
from apps.stock.serializers import BatchCreateFromFrontendSerializer, BatchReadSerializer

logger = logging.getLogger(__name__)

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
        queryset = SupplyBatch.objects.select_related('supply').all()
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
                alerts.append({"supply_id": supply.id, "supply_name": supply.name, "supply_sku": supply.sku, "alert_type": "LOW_STOCK", "severity": "critical", "message": f"CRÍTICO: '{supply.name}' tiene {active_stock} uds.", "current_value": active_stock})
            elif active_stock <= warning_threshold:
                alerts.append({"supply_id": supply.id, "supply_name": supply.name, "supply_sku": supply.sku, "alert_type": "LOW_STOCK", "severity": "warning", "message": f"ALERTA: '{supply.name}' tiene {active_stock} uds.", "current_value": active_stock})

        limit_date = today + datetime.timedelta(days=45)
        expiring_batches = SupplyBatch.objects.filter(expiration_date__gt=today, expiration_date__lte=limit_date, current_stock__gt=0).select_related('supply')

        for batch in expiring_batches:
            days_remaining = (batch.expiration_date - today).days
            severity = 'critical' if days_remaining <= 15 else 'warning'
            
            alerts.append({"supply_id": batch.supply.id, "supply_name": batch.supply.name, "supply_sku": batch.supply.sku, "alert_type": "NEAR_EXPIRATION", "severity": severity, "message": f"Lote '{batch.lot_number}' vence en {days_remaining} días.", "current_value": batch.current_stock})

        alerts.sort(key=lambda a: 0 if a['severity'] == 'critical' else 1)
        return Response({"alerts": alerts})