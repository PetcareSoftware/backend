from django.utils import timezone
from .models import Appointment


class AppointmentSelector:
    @staticmethod
    def get_today(vet=None):
        today = timezone.localdate()
        qs = Appointment.objects.filter(slot__date=today).select_related('pet__breed__species', 'vet__user__user', 'slot')
        if vet:
            qs = qs.filter(vet=vet)
        return qs.order_by('slot__start_time')

    @staticmethod
    def get_history(pet=None, owner=None, status=None):
        qs = Appointment.objects.select_related('pet__breed__species', 'vet__user__user', 'slot')
        if pet:
            qs = qs.filter(pet=pet)
        if owner:
            qs = qs.filter(pet__owner=owner)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-scheduled_at')

    @staticmethod
    def get_by_id(pk):
        return Appointment.objects.select_related('pet__owner__user', 'vet__user__user', 'slot').get(pk=pk)
