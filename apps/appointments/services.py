from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone
from apps.common.exceptions import BusinessRuleError, PetNotOwnedByUserError, SlotNotAvailableError
from apps.common.roles import OWNER, RECEPTIONIST, VET, has_role
from apps.common.utils import aware_datetime_for_slot
from apps.pets.models import Pet
from apps.schedules.models import TimeSlot
from apps.schedules.services import AvailabilityService
from .models import Appointment, WaitingListEntry


class AppointmentService:
    @staticmethod
    @transaction.atomic
    def create(*, actor, pet_id, vet, slot_id, reason, notes=''):
        try:
            pet = Pet.objects.select_related('owner').get(id=pet_id)
        except Pet.DoesNotExist as exc:
            raise BusinessRuleError('Mascota inválida o eliminada.', status_code=400) from exc
        if has_role(actor, OWNER) and str(pet.owner_id) != str(actor.id):
            raise PetNotOwnedByUserError()
        if not has_role(actor, OWNER, RECEPTIONIST):
            raise BusinessRuleError('No tienes permiso para agendar citas.', status_code=403)
        if vet.account.role_name != VET or not vet.account.is_active:
            raise BusinessRuleError('El veterinario no está activo.', status_code=400)
        try:
            slot = TimeSlot.objects.select_for_update().get(id=slot_id, vet=vet)
        except TimeSlot.DoesNotExist as exc:
            raise BusinessRuleError('Slot inválido para el veterinario indicado.', status_code=400) from exc
        AppointmentService._validate_future_slot(slot)
        if slot.status != TimeSlot.Status.FREE:
            raise SlotNotAvailableError()
        try:
            appointment = Appointment.objects.create(
                pet=pet,
                vet=vet,
                slot=slot,
                reason=reason,
                notes=notes or '',
                status=Appointment.Status.SCHEDULED,
                scheduled_at=aware_datetime_for_slot(slot.date, slot.start_time),
            )
            AvailabilityService.block_slot(slot)
        except IntegrityError as exc:
            raise SlotNotAvailableError('Ya existe una cita activa para ese slot.') from exc
        return appointment

    @staticmethod
    @transaction.atomic
    def update(*, actor, appointment, new_slot_id=None, reason=None, notes=None):
        AppointmentService.ensure_can_manage(actor, appointment, owner_allowed=True, receptionist_allowed=True, vet_allowed=False)
        if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
            raise BusinessRuleError('No se puede modificar una cita completada o cancelada.')
        if new_slot_id and str(new_slot_id) != str(appointment.slot_id):
            old_slot = TimeSlot.objects.select_for_update().get(id=appointment.slot_id)
            try:
                new_slot = TimeSlot.objects.select_for_update().get(id=new_slot_id, vet=appointment.vet)
            except TimeSlot.DoesNotExist as exc:
                raise BusinessRuleError('Nuevo slot inválido.', status_code=400) from exc
            AppointmentService._validate_future_slot(new_slot)
            if new_slot.status != TimeSlot.Status.FREE:
                raise SlotNotAvailableError()
            old_slot.status = TimeSlot.Status.FREE
            old_slot.save(update_fields=['status'])
            new_slot.status = TimeSlot.Status.BOOKED
            new_slot.save(update_fields=['status'])
            appointment.slot = new_slot
            appointment.scheduled_at = aware_datetime_for_slot(new_slot.date, new_slot.start_time)
        if reason is not None:
            appointment.reason = reason
        if notes is not None:
            appointment.notes = notes
        appointment.save()
        return appointment

    @staticmethod
    @transaction.atomic
    def cancel(*, actor, appointment, cancellation_reason=''):
        AppointmentService.ensure_can_manage(actor, appointment, owner_allowed=True, receptionist_allowed=True, vet_allowed=False)
        appointment = Appointment.objects.select_for_update().select_related('slot').get(id=appointment.id)
        if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
            raise BusinessRuleError('La cita ya está completada o cancelada y no puede cancelarse.')
        slot = TimeSlot.objects.select_for_update().get(id=appointment.slot_id)
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancelled_at = timezone.now()
        appointment.cancellation_reason = cancellation_reason or ''
        appointment.save(update_fields=['status', 'cancelled_at', 'cancellation_reason'])
        AvailabilityService.release_slot(slot)
        return appointment

    @staticmethod
    @transaction.atomic
    def confirm(*, actor, appointment):
        AppointmentService.ensure_can_manage(actor, appointment, owner_allowed=True, receptionist_allowed=True, vet_allowed=False)
        if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
            raise BusinessRuleError('No se puede confirmar una cita completada o cancelada.')
        if appointment.status != Appointment.Status.SCHEDULED:
            raise BusinessRuleError('Solo se puede confirmar una cita en estado SCHEDULED.')
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save(update_fields=['status'])
        return appointment

    @staticmethod
    @transaction.atomic
    def check_in(*, actor, appointment):
        if not has_role(actor, RECEPTIONIST):
            raise BusinessRuleError('Solo recepción puede hacer check-in.', status_code=403)
        appointment = Appointment.objects.select_for_update().select_related('slot').get(id=appointment.id)
        if WaitingListEntry.objects.filter(appointment=appointment).exists():
            raise BusinessRuleError('La cita ya tiene check-in registrado.', status_code=409)
        if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
            raise BusinessRuleError('La cita está completada o cancelada y no admite check-in.')
        if appointment.status not in [Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED]:
            raise BusinessRuleError('Solo se puede hacer check-in a citas SCHEDULED o CONFIRMED.')
        today = timezone.localdate()
        if appointment.slot.date != today:
            raise BusinessRuleError('Solo se puede hacer check-in a citas del día actual.')
        entry = AppointmentService._create_waiting_entry_with_position(appointment)
        appointment.status = Appointment.Status.CHECKED_IN
        appointment.save(update_fields=['status'])
        return entry

    @staticmethod
    @transaction.atomic
    def call_next(*, actor, entry):
        if not has_role(actor, RECEPTIONIST, VET):
            raise BusinessRuleError('Solo recepción o veterinario pueden llamar al siguiente paciente.', status_code=403)
        if has_role(actor, VET) and str(entry.appointment.vet_id) != str(actor.id):
            raise BusinessRuleError('El veterinario solo puede llamar pacientes de su propia cola.', status_code=403)
        queue = WaitingListEntry.objects.select_for_update().filter(
            vet=entry.vet,
            queue_date=entry.queue_date,
            called_at__isnull=True,
        ).order_by('arrived_at', 'position')
        next_entry = queue.first()
        if not next_entry or next_entry.id != entry.id:
            raise BusinessRuleError('Solo se puede llamar al siguiente paciente real de la cola.')
        entry.called_at = timezone.now()
        entry.save(update_fields=['called_at'])
        return entry

    @staticmethod
    def complete(*, actor, appointment):
        if not has_role(actor, VET) or str(appointment.vet_id) != str(actor.id):
            raise BusinessRuleError('Solo el veterinario asignado puede completar la cita.', status_code=403)
        if not hasattr(appointment, 'consultation'):
            raise BusinessRuleError('No se puede completar una cita sin consulta clínica asociada.')
        appointment.status = Appointment.Status.COMPLETED
        appointment.save(update_fields=['status'])
        return appointment

    @staticmethod
    def _create_waiting_entry_with_position(appointment):
        queue_date = appointment.slot.date
        for _ in range(5):
            try:
                with transaction.atomic():
                    same_queue = WaitingListEntry.objects.select_for_update().filter(
                        vet=appointment.vet,
                        queue_date=queue_date,
                    )
                    next_position = (same_queue.aggregate(max_pos=Max('position'))['max_pos'] or 0) + 1
                    return WaitingListEntry.objects.create(
                        appointment=appointment,
                        vet=appointment.vet,
                        queue_date=queue_date,
                        position=next_position,
                    )
            except IntegrityError:
                continue
        raise BusinessRuleError('No se pudo asignar una posición única en la lista de espera.', status_code=409)

    @staticmethod
    def ensure_can_manage(actor, appointment, *, owner_allowed=True, receptionist_allowed=True, vet_allowed=False):
        if receptionist_allowed and has_role(actor, RECEPTIONIST):
            return True
        if owner_allowed and has_role(actor, OWNER) and str(appointment.pet.owner_id) == str(actor.id):
            return True
        if vet_allowed and has_role(actor, VET) and str(appointment.vet_id) == str(actor.id):
            return True
        raise BusinessRuleError('No tienes permiso sobre esta cita.', status_code=403)

    @staticmethod
    def _validate_future_slot(slot):
        today = timezone.localdate()
        if slot.date < today or (slot.date == today and slot.start_time <= timezone.localtime().time()):
            raise BusinessRuleError('No se puede usar un slot pasado.', status_code=400)
