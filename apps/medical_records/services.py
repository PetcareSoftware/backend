from datetime import timedelta
from django.db import IntegrityError, transaction
from django.utils import timezone
from apps.appointments.models import Appointment
from apps.common.exceptions import BusinessRuleError
from integrations.inventory_client import InventoryClient, InventoryInsufficientStock, InventoryNotFound, InventoryUnavailable
from .models import Consultation, MedicalAttachment, Prescription, SupplyUsed, Treatment


class ConsultationService:
    @staticmethod
    @transaction.atomic
    def register(*, appointment, vet, diagnosis, clinical_notes='', treatments=None, prescriptions=None):
        if str(appointment.vet_id) != str(vet.user_id):
            raise BusinessRuleError('El veterinario no está asignado a esta cita.', status_code=403)
        if Consultation.objects.filter(appointment=appointment).exists():
            raise BusinessRuleError('Ya existe una consulta registrada para esta cita.', status_code=409)
        if appointment.status != Appointment.Status.CHECKED_IN:
            raise BusinessRuleError('La cita debe estar en estado CHECKED_IN para registrar consulta.')
        try:
            consultation = Consultation.objects.create(
                medical_record=appointment.pet.medical_record,
                appointment=appointment,
                vet=vet,
                diagnosis=diagnosis,
                clinical_notes=clinical_notes or '',
            )
        except IntegrityError as exc:
            raise BusinessRuleError('Ya existe una consulta registrada para esta cita.', status_code=409) from exc
        for data in treatments or []:
            Treatment.objects.create(consultation=consultation, **data)
        for data in prescriptions or []:
            Prescription.objects.create(consultation=consultation, **data)
        return consultation

    @staticmethod
    def assert_owner_vet(consultation, vet):
        if str(consultation.vet_id) != str(vet.user_id):
            raise BusinessRuleError('Solo el veterinario que registró la consulta puede modificarla.', status_code=403)

    @staticmethod
    def assert_edit_window(consultation):
        if timezone.now() - consultation.created_at > timedelta(hours=24):
            raise BusinessRuleError('La consulta tiene más de 24 horas y es de solo lectura.', status_code=403)

    @staticmethod
    @transaction.atomic
    def add_prescription(*, consultation, vet, data):
        ConsultationService.assert_owner_vet(consultation, vet)
        ConsultationService.assert_edit_window(consultation)
        return Prescription.objects.create(consultation=consultation, **data)

    @staticmethod
    @transaction.atomic
    def attach_file(*, consultation, vet, data):
        ConsultationService.assert_owner_vet(consultation, vet)
        ConsultationService.assert_edit_window(consultation)
        return MedicalAttachment.objects.create(consultation=consultation, **data)

    @staticmethod
    @transaction.atomic
    def register_supplies(*, consultation, vet, supplies):
        ConsultationService.assert_owner_vet(consultation, vet)
        client = InventoryClient()
        try:
            checked = [client.check_availability(item['supply_id'], item['quantity']) for item in supplies]
            deducted = [client.deduct_stock(item['supply_id'], item['quantity'], ref_id=consultation.id) for item in supplies]
        except InventoryNotFound as exc:
            raise BusinessRuleError(str(exc), status_code=404) from exc
        except InventoryInsufficientStock as exc:
            raise BusinessRuleError(str(exc), status_code=409) from exc
        except InventoryUnavailable:
            created = [SupplyUsed.objects.create(
                consultation=consultation,
                supply_id=item['supply_id'],
                quantity=item['quantity'],
                sync_status=SupplyUsed.SyncStatus.PENDING_SYNC,
            ) for item in supplies]
            from .tasks import retry_pending_supply_sync
            try:
                retry_pending_supply_sync.delay()
            except Exception:
                pass
            return created
        by_id = {str(item.get('supply_id')): item for item in checked + deducted if item}
        return [SupplyUsed.objects.create(
            consultation=consultation,
            supply_id=item['supply_id'],
            supply_name=by_id.get(str(item['supply_id']), {}).get('name'),
            unit_cost=by_id.get(str(item['supply_id']), {}).get('unit_cost'),
            quantity=item['quantity'],
            sync_status=SupplyUsed.SyncStatus.SYNCED,
        ) for item in supplies]
