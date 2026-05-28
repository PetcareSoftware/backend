import uuid
from django.db import transaction
from django.utils import timezone
from apps.common.exceptions import BusinessRuleError
from apps.users.models import Veterinarian
from integrations.inventory_client import InventoryClient, InventoryInsufficientStock, InventoryNotFound, InventoryUnavailable
from .models import VaccinationEvent, VaccinationPlan, VaccinationPlanItem


class VaccinationService:
    @staticmethod
    @transaction.atomic
    def create_plan(*, patient, vet_user, data):
        vet = Veterinarian.objects.get(user_id=vet_user.id)
        VaccinationPlan.objects.filter(patient=patient, is_active=True).update(is_active=False)
        items = data.pop('items', [])
        plan = VaccinationPlan.objects.create(patient=patient, created_by=vet, notes=data.get('notes') or '', is_active=True)
        for item in items:
            VaccinationPlanItem.objects.create(plan=plan, **item)
        return plan

    @staticmethod
    def schedule(*, patient):
        plan = patient.vaccination_plans.filter(is_active=True).prefetch_related('items__events').first()
        if not plan:
            return []
        today = timezone.localdate()
        result = []
        # IMPORTANTE: item.events.first() NO usa el caché de prefetch_related y
        # genera una query adicional por cada ítem del plan. Django sí reutiliza
        # el caché para item.events.all(), por eso se materializa la lista aquí.
        for item in plan.items.all().order_by('scheduled_date'):
            events = list(item.events.all())
            event = events[0] if events else None
            status = 'APPLIED' if event else ('OVERDUE' if item.scheduled_date < today else 'PENDING')
            result.append({
                'id': str(item.id),
                'vaccine_name': item.vaccine_name,
                'scheduled_date': item.scheduled_date,
                'supply_id': str(item.supply_id) if item.supply_id else None,
                'status': status,
                'event_id': str(event.id) if event else None,
            })
        return result

    @staticmethod
    @transaction.atomic
    def register_event(*, patient, vet_user, data):
        vet = Veterinarian.objects.get(user_id=vet_user.id)
        if data.get('plan_item_id'):
            try:
                data['plan_item'] = VaccinationPlanItem.objects.get(id=data.pop('plan_item_id'), plan__patient=patient)
            except VaccinationPlanItem.DoesNotExist as exc:
                raise BusinessRuleError('plan_item_id inválido para esta mascota.', status_code=400) from exc
        event_id = uuid.uuid4()
        supply_id = data.get('supply_id')
        quantity = data.get('quantity_used')
        sync_status = VaccinationEvent.SyncStatus.SYNCED
        if supply_id:
            client = InventoryClient()
            try:
                client.check_availability(supply_id, quantity)
                client.deduct_stock(supply_id, quantity, ref_id=event_id)
            except InventoryNotFound as exc:
                raise BusinessRuleError(str(exc), status_code=404) from exc
            except InventoryInsufficientStock as exc:
                raise BusinessRuleError(str(exc), status_code=409) from exc
            except InventoryUnavailable:
                sync_status = VaccinationEvent.SyncStatus.PENDING_SYNC
        return VaccinationEvent.objects.create(id=event_id, patient=patient, created_by=vet, sync_status=sync_status, **data)
