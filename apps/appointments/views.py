from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from apps.common.roles import OWNER, RECEPTIONIST, VET, has_role
from apps.users.models import Veterinarian
from .models import Appointment, WaitingListEntry
from .selectors import AppointmentSelector
from .serializers import AppointmentCancelSerializer, AppointmentCreateSerializer, AppointmentSerializer, AppointmentUpdateSerializer, WaitingListSerializer
from .services import AppointmentService


def waiting_entry_summary(entry):
    return {
        'id': str(entry.id),
        'position': entry.position,
        'arrived_at': entry.arrived_at,
        'called_at': entry.called_at,
    }


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('pet__owner__user', 'pet__breed__species', 'vet__user__user', 'slot')

    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        if self.action in {'partial_update', 'update'}:
            return AppointmentUpdateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qp = self.request.query_params
        # Filtrado por rol solo para listados; en detalle se obtiene el objeto para poder devolver 403 y no 404.
        if self.action == 'list':
            if has_role(self.request.user, OWNER):
                qs = qs.filter(pet__owner_id=self.request.user.id)
            elif has_role(self.request.user, VET):
                qs = qs.filter(vet_id=self.request.user.id)
        if qp.get('date'):
            qs = qs.filter(slot__date=qp['date'])
        if qp.get('vet'):
            qs = qs.filter(vet_id=qp['vet'])
        if qp.get('status'):
            qs = qs.filter(status=qp['status'])
        if qp.get('pet'):
            qs = qs.filter(pet_id=qp['pet'])
        return qs

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if self.action in {'retrieve', 'partial_update', 'update'}:
            AppointmentService.ensure_can_manage(request.user, obj, owner_allowed=True, receptionist_allowed=True, vet_allowed=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        vet_id = data.pop('vet_id')
        try:
            vet = Veterinarian.objects.select_related('user__user').get(user_id=vet_id, user__user__is_active=True, user__user__role__name=VET)
        except Veterinarian.DoesNotExist as exc:
            raise NotFound('El vet_id no corresponde a ningún veterinario activo.') from exc
        appointment = AppointmentService.create(actor=request.user, vet=vet, **data)
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        appointment = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        if 'slot_id' in data:
            data['new_slot_id'] = data.pop('slot_id')
        appointment = AppointmentService.update(actor=request.user, appointment=appointment, **data)
        return Response(AppointmentSerializer(appointment).data)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AppointmentService.cancel(actor=request.user, appointment=appointment, cancellation_reason=serializer.validated_data.get('cancellation_reason', ''))
        return Response({'id': str(appointment.id), 'status': appointment.status, 'cancelled_at': appointment.cancelled_at, 'cancellation_reason': appointment.cancellation_reason})

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        appointment = AppointmentService.confirm(actor=request.user, appointment=self.get_object())
        return Response({'id': str(appointment.id), 'status': appointment.status, 'scheduled_at': appointment.scheduled_at})

    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        entry = AppointmentService.check_in(actor=request.user, appointment=self.get_object())
        return Response({
            'appointment_id': str(entry.appointment_id),
            'status': Appointment.Status.CHECKED_IN,
            'waiting_entry': waiting_entry_summary(entry),
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = AppointmentService.complete(actor=request.user, appointment=self.get_object())
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=['post'])
    def consultations(self, request, pk=None):
        from apps.medical_records.serializers import ConsultationCreateSerializer, ConsultationSerializer
        from apps.medical_records.services import ConsultationService
        if not has_role(request.user, VET):
            raise PermissionDenied('Solo un veterinario puede registrar consultas.')
        appointment = self.get_object()
        serializer = ConsultationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vet = Veterinarian.objects.get(user_id=request.user.id)
        consultation = ConsultationService.register(appointment=appointment, vet=vet, **serializer.validated_data)
        return Response(ConsultationSerializer(consultation, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def today(self, request):
        if has_role(request.user, RECEPTIONIST):
            qs = AppointmentSelector.get_today()
        elif has_role(request.user, VET):
            try:
                vet = Veterinarian.objects.get(user_id=request.user.id)
            except Veterinarian.DoesNotExist as exc:
                raise NotFound('El vet_id no corresponde a ningún veterinario activo.') from exc
            qs = AppointmentSelector.get_today(vet=vet)
        else:
            raise PermissionDenied('Solo recepcion o veterinarios pueden consultar citas del dia.')
        return Response(AppointmentSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path=r'today/by-vet/(?P<vet_id>[^/.]+)')
    def today_by_vet(self, request, vet_id=None):
        if has_role(request.user, VET) and str(request.user.id) != str(vet_id):
            raise PermissionDenied('El veterinario solo puede consultar su propia agenda del día.')
        if not has_role(request.user, VET, RECEPTIONIST):
            raise PermissionDenied('Solo recepción o veterinarios pueden consultar la agenda por veterinario.')
        try:
            vet = Veterinarian.objects.get(user_id=vet_id)
        except Veterinarian.DoesNotExist as exc:
            raise NotFound('El vet_id no corresponde a ningún veterinario activo.') from exc
        qs = AppointmentSelector.get_today(vet=vet)
        return Response({
            'vet': {'id': str(vet.user_id), 'full_name': vet.full_name},
            'date': timezone.localdate().isoformat(),
            'appointments': AppointmentSerializer(qs, many=True).data,
        })


class WaitingListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = WaitingListEntry.objects.select_related('appointment__pet__breed__species', 'appointment__vet__user__user', 'appointment__slot', 'vet__user__user')
    serializer_class = WaitingListSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(queue_date=timezone.localdate()).order_by('arrived_at')
        vet_id = self.request.query_params.get('vet_id') or self.request.query_params.get('vet')
        if vet_id:
            qs = qs.filter(vet_id=vet_id)
        if has_role(self.request.user, VET):
            qs = qs.filter(vet_id=self.request.user.id)
        return qs

    def list(self, request, *args, **kwargs):
        if not has_role(request.user, RECEPTIONIST, VET):
            raise PermissionDenied('Solo recepción o veterinarios pueden ver la lista de espera.')
        qs = self.filter_queryset(self.get_queryset())
        queue_date = timezone.localdate()
        return Response({'date': queue_date.isoformat(), 'entries': WaitingListSerializer(qs, many=True).data})

    @action(detail=True, methods=['post'], url_path='call-next')
    def call_next(self, request, pk=None):
        entry = AppointmentService.call_next(actor=request.user, entry=self.get_object())
        return Response(WaitingListSerializer(entry).data)
