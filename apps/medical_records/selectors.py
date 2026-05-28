from django.db.models import Prefetch
from datetime import timedelta
from django.utils import timezone
from .models import Consultation, MedicalRecord


class MedicalRecordSelector:
    @staticmethod
    def get_full_record(pet):
        consultations = Consultation.objects.select_related('vet__user__user', 'appointment').prefetch_related(
            'treatments', 'prescriptions', 'attachments', 'supplies_used'
        )
        return MedicalRecord.objects.select_related('patient__breed__species', 'patient__owner__user').prefetch_related(
            Prefetch('consultations', queryset=consultations)
        ).get(patient=pet)

    @staticmethod
    def get_current_status(pet):
        record = MedicalRecordSelector.get_full_record(pet)
        consultations = list(record.consultations.all())
        last = consultations[0] if consultations else None
        today = timezone.localdate()
        active_treatments = []
        for consultation in consultations:
            for treatment in consultation.treatments.all():
                if treatment.start_date and treatment.duration_days:
                    ends_at = treatment.start_date + timedelta(days=treatment.duration_days)
                    if ends_at >= today:
                        active_treatments.append({'name': treatment.name, 'ends_at': ends_at})
        return record, last, active_treatments
