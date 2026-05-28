from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from apps.common.roles import OWNER, RECEPTIONIST, VET, has_role
from apps.users.models import Veterinarian
from .models import Consultation, MedicalRecord
from .selectors import MedicalRecordSelector
from .serializers import (
    ConsultationSerializer,
    ConsultationUpdateSerializer,
    MedicalAttachmentSerializer,
    MedicalRecordSerializer,
    PrescriptionSerializer,
    SupplyUsedSerializer,
    SuppliesUsedRequestSerializer,
)
from .services import ConsultationService


class ConsultationViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Consultation.objects.select_related(
        'medical_record__patient__owner__user', 'appointment', 'vet__user__user'
    ).prefetch_related('treatments', 'prescriptions', 'attachments', 'supplies_used')

    def get_serializer_class(self):
        return ConsultationUpdateSerializer if self.action in {'partial_update', 'update'} else ConsultationSerializer

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if has_role(request.user, OWNER) and str(obj.medical_record.patient.owner_id) != str(request.user.id):
            raise PermissionDenied('No puedes ver la consulta de una mascota ajena.')
        if self.action in {'partial_update', 'update', 'prescriptions', 'attachments', 'supplies_used'}:
            if not has_role(request.user, VET):
                raise PermissionDenied('Solo veterinarios pueden modificar la consulta.')
            if str(obj.vet_id) != str(request.user.id):
                raise PermissionDenied('Solo el veterinario que registró la consulta puede modificarla.')

    def retrieve(self, request, *args, **kwargs):
        consultation = self.get_object()
        return Response(ConsultationSerializer(consultation, context={'request': request}).data)

    def partial_update(self, request, *args, **kwargs):
        consultation = self.get_object()
        serializer = ConsultationUpdateSerializer(consultation, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ConsultationSerializer(consultation, context={'request': request}).data)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def prescriptions(self, request, pk=None):
        consultation = self.get_object()
        vet = Veterinarian.objects.get(user_id=request.user.id)
        serializer = PrescriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prescription = ConsultationService.add_prescription(consultation=consultation, vet=vet, data=serializer.validated_data)
        return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def attachments(self, request, pk=None):
        consultation = self.get_object()
        vet = Veterinarian.objects.get(user_id=request.user.id)
        serializer = MedicalAttachmentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        attachment = ConsultationService.attach_file(consultation=consultation, vet=vet, data=serializer.validated_data)
        return Response(MedicalAttachmentSerializer(attachment, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='supplies-used')
    def supplies_used(self, request, pk=None):
        consultation = self.get_object()
        vet = Veterinarian.objects.get(user_id=request.user.id)
        serializer = SuppliesUsedRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supplies = [dict(item) for item in serializer.validated_data['supplies']]
        created = ConsultationService.register_supplies(consultation=consultation, vet=vet, supplies=supplies)
        return Response({'results': SupplyUsedSerializer(created, many=True).data}, status=status.HTTP_201_CREATED)


class MedicalRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MedicalRecord.objects.select_related('patient__owner__user', 'patient__breed__species').prefetch_related('consultations')
    serializer_class = MedicalRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if has_role(self.request.user, OWNER):
            return qs.filter(patient__owner_id=self.request.user.id)
        if has_role(self.request.user, VET, RECEPTIONIST):
            return qs
        return qs.none()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if has_role(request.user, OWNER) and str(obj.patient.owner_id) != str(request.user.id):
            raise PermissionDenied('No puedes ver el expediente de una mascota ajena.')
        if not has_role(request.user, OWNER, VET, RECEPTIONIST):
            raise PermissionDenied('No tienes permiso para consultar expedientes clínicos.')


def serialize_medical_record_for_pet(request, pet):
    record = MedicalRecordSelector.get_full_record(pet)
    return MedicalRecordSerializer(record, context={'request': request}).data


def serialize_medical_record_summary(pet):
    record, last, active_treatments = MedicalRecordSelector.get_current_status(pet)
    next_due = None
    status_text = 'SIN_PLAN'
    active_plan = pet.vaccination_plans.filter(is_active=True).prefetch_related('items__events').first()
    if active_plan:
        pending_items = sorted([i for i in active_plan.items.all() if not list(i.events.all())], key=lambda i: i.scheduled_date)
        if pending_items:
            next_due = pending_items[0].scheduled_date
            status_text = 'VENCIDAS' if next_due < timezone.localdate() else 'AL_DIA'
        else:
            status_text = 'AL_DIA'
    return {
        'pet': {
            'id': str(pet.id),
            'name': pet.name,
            'species': pet.breed.species.name if pet.breed_id else None,
            'breed': pet.breed.name if pet.breed_id else None,
            'weight_kg': str(pet.weight_kg) if pet.weight_kg is not None else None,
            'sex': pet.sex,
        },
        'last_consultation': {
            'id': str(last.id),
            'date': last.date,
            'diagnosis': last.diagnosis,
            'vet': last.vet.full_name,
        } if last else None,
        'active_treatments': active_treatments,
        'vaccination_status': status_text,
        'next_vaccine_due': next_due,
        'total_consultations': len(list(record.consultations.all())),
    }
