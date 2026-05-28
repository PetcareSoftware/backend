from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from apps.common.exceptions import BusinessRuleError
from .models import TimeSlot, VetSchedule


class AvailabilityService:
    @staticmethod
    def _iter_slot_ranges(schedule):
        current = datetime.combine(timezone.localdate(), schedule.start_time)
        end = datetime.combine(timezone.localdate(), schedule.end_time)
        delta = timedelta(minutes=schedule.slot_duration_min)
        while current + delta <= end:
            yield current.time(), (current + delta).time()
            current += delta

    @staticmethod
    @transaction.atomic
    def generate_slots(vet, date_from, date_to):
        """Idempotente: no duplica slots existentes."""
        if date_to < date_from:
            raise BusinessRuleError('El rango de fechas es inválido.')
        created = []
        day = date_from
        while day <= date_to:
            schedules = VetSchedule.objects.filter(vet=vet, day_of_week=day.weekday(), is_active=True)
            for schedule in schedules:
                for start, end in AvailabilityService._iter_slot_ranges(schedule):
                    slot, was_created = TimeSlot.objects.get_or_create(
                        vet=vet, date=day, start_time=start, end_time=end,
                        defaults={'status': TimeSlot.Status.FREE},
                    )
                    if was_created:
                        created.append(slot)
            day += timedelta(days=1)
        return created

    @staticmethod
    def enqueue_generation(vet, date_from, date_to):
        from .tasks import generate_slots_for_vet_range
        def _enqueue():
            try:
                generate_slots_for_vet_range.delay(str(vet.user_id), date_from.isoformat(), date_to.isoformat())
            except Exception:
                # El request nunca debe fallar por indisponibilidad del broker Celery.
                pass
        transaction.on_commit(_enqueue)

    @staticmethod
    def get_available_slots(vet, date):
        today = timezone.localdate()
        if date < today:
            return TimeSlot.objects.none()
        qs = TimeSlot.objects.filter(vet=vet, date=date, status=TimeSlot.Status.FREE).order_by('start_time')
        if date == today:
            now_time = timezone.localtime().time()
            qs = qs.filter(start_time__gt=now_time)
        return qs

    @staticmethod
    def block_slot(slot):
        if slot.status != TimeSlot.Status.FREE:
            raise BusinessRuleError('El slot no está libre.', status_code=409)
        slot.status = TimeSlot.Status.BOOKED
        slot.save(update_fields=['status'])
        return slot

    @staticmethod
    def release_slot(slot):
        slot.status = TimeSlot.Status.FREE
        slot.save(update_fields=['status'])
        return slot

    @staticmethod
    def validate_range(date_from, date_to):
        if date_to < date_from:
            raise BusinessRuleError('El rango de fechas es inválido.', status_code=400)
        if (date_to - date_from).days > 30:
            raise BusinessRuleError('El rango máximo permitido es de 30 días.', status_code=400)
