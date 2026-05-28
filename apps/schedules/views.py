from datetime import timedelta
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.response import Response
from apps.common.roles import MANAGER, RECEPTIONIST, VET, has_role
from apps.appointments.serializers import WaitingListSerializer
from apps.users.models import Veterinarian
from .models import TimeSlot, VetSchedule
from .serializers import TimeSlotSerializer, VetScheduleSerializer, VetSerializer
from .services import AvailabilityService


def parse_date_or_today(value):
    if not value:
        return timezone.localdate()
    from datetime import date
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ParseError('Formato de fecha inválido. Use YYYY-MM-DD.') from exc


class VetViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'user_id'
    queryset = Veterinarian.objects.select_related('user__user').filter(user__user__is_active=True, user__user__role__name=VET)
    serializer_class = VetSerializer

    @action(detail=True, methods=['get'])
    def slots(self, request, user_id=None):
        vet = self.get_object()  # query 1
        requested_date = parse_date_or_today(request.query_params.get('date'))
        qs = AvailabilityService.get_available_slots(vet, requested_date)  # query 2 on serialization
        return Response({'vet': VetSerializer(vet).data, 'date': requested_date.isoformat(), 'slots': TimeSlotSerializer(qs, many=True).data})

    @action(detail=True, methods=['get'])
    def availability(self, request, user_id=None):
        vet = self.get_object()
        date_from = parse_date_or_today(request.query_params.get('from'))
        date_to = parse_date_or_today(request.query_params.get('to')) if request.query_params.get('to') else date_from
        AvailabilityService.validate_range(date_from, date_to)
        slots = TimeSlot.objects.filter(vet=vet, date__gte=max(date_from, timezone.localdate()), date__lte=date_to)
        data = {}
        for row in slots.values('date').annotate(
            available_slots=Count('id', filter=Q(status=TimeSlot.Status.FREE)),
            booked_slots=Count('id', filter=Q(status=TimeSlot.Status.BOOKED)),
        ).order_by('date'):
            data[row['date'].isoformat()] = {'available_slots': row['available_slots'], 'booked_slots': row['booked_slots']}
        return Response({'vet': VetSerializer(vet).data, 'from': date_from.isoformat(), 'to': date_to.isoformat(), 'days': data})

    @action(detail=True, methods=['post'])
    def schedules(self, request, user_id=None):
        vet = self.get_object()
        if not (has_role(request.user, MANAGER) or (has_role(request.user, VET) and str(request.user.id) == str(vet.user_id))):
            raise PermissionDenied('Solo el propio veterinario o un administrador pueden modificar horarios.')
        serializer = VetScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save(vet=vet)
        # Pre-generación fuera de GET /slots/ para mantener ese endpoint en <=2 queries y no bloquear la consulta de slots.
        if settings.AUTO_GENERATE_SLOTS_ON_SCHEDULE_SAVE:
            today = timezone.localdate()
            AvailabilityService.enqueue_generation(vet, today, today + timedelta(days=30))
        return Response(VetScheduleSerializer(schedule).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='waiting-list')
    def waiting_list(self, request, user_id=None):
        from apps.appointments.models import WaitingListEntry
        vet = self.get_object()
        if has_role(request.user, VET) and str(request.user.id) != str(vet.user_id):
            raise PermissionDenied('El veterinario solo puede consultar su propia lista de espera.')
        if not has_role(request.user, VET, RECEPTIONIST):
            raise PermissionDenied('Solo recepción o el veterinario asignado pueden ver la lista de espera.')
        queue_date = timezone.localdate()
        qs = WaitingListEntry.objects.filter(
            vet=vet,
            queue_date=queue_date,
        ).select_related('appointment__pet__breed__species', 'appointment__vet__user__user', 'appointment__slot', 'vet__user__user').order_by('arrived_at')
        return Response({'date': queue_date.isoformat(), 'entries': WaitingListSerializer(qs, many=True).data})


class ScheduleViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = VetSchedule.objects.select_related('vet__user__user')
    serializer_class = VetScheduleSerializer

    def partial_update(self, request, *args, **kwargs):
        schedule = self.get_object()
        vet = schedule.vet
        if not (has_role(request.user, MANAGER) or (has_role(request.user, VET) and str(request.user.id) == str(vet.user_id))):
            raise PermissionDenied('Solo el propio veterinario o un administrador pueden modificar horarios.')
        response = super().partial_update(request, *args, **kwargs)
        if settings.AUTO_GENERATE_SLOTS_ON_SCHEDULE_SAVE:
            today = timezone.localdate()
            AvailabilityService.enqueue_generation(vet, today, today + timedelta(days=30))
        return response

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        today = timezone.localdate()
        date_from = parse_date_or_today(request.query_params.get('from'))
        date_to = parse_date_or_today(request.query_params.get('to')) if request.query_params.get('to') else date_from
        AvailabilityService.validate_range(date_from, date_to)
        vets = Veterinarian.objects.select_related('user__user').filter(user__user__is_active=True, user__user__role__name=VET)
        slots = TimeSlot.objects.filter(vet__in=vets, date__gte=max(date_from, today), date__lte=date_to)
        result = []
        for vet in vets:
            days = {}
            for row in slots.filter(vet=vet).values('date').annotate(
                available_slots=Count('id', filter=Q(status=TimeSlot.Status.FREE)),
                booked_slots=Count('id', filter=Q(status=TimeSlot.Status.BOOKED)),
            ).order_by('date'):
                days[row['date'].isoformat()] = {'available_slots': row['available_slots'], 'booked_slots': row['booked_slots']}
            result.append({'id': str(vet.user_id), 'full_name': vet.full_name, 'days': days})
        return Response({'from': date_from.isoformat(), 'to': date_to.isoformat(), 'vets': result})
