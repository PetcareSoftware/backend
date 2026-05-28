from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from apps.common.roles import OWNER, VET, MANAGER, has_role
from apps.appointments.serializers import AppointmentSerializer
from apps.medical_records.views import serialize_medical_record_for_pet, serialize_medical_record_summary
from apps.vaccinations.serializers import VaccinationEventSerializer, VaccinationPlanCreateSerializer, VaccinationPlanSerializer
from apps.vaccinations.services import VaccinationService
from .models import Breed, Pet, Species
from .serializers import BreedSerializer, PetSerializer, PetUpdateSerializer, SpeciesSerializer
from .services import PetService


class CatalogWriteMixin:
    def check_permissions(self, request):
        super().check_permissions(request)
        if request.method not in {'GET', 'HEAD', 'OPTIONS'} and not has_role(request.user, MANAGER):
            raise PermissionDenied('Solo gerencia puede administrar catálogos clínicos.')


class SpeciesViewSet(CatalogWriteMixin, viewsets.ModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer


class BreedViewSet(CatalogWriteMixin, viewsets.ModelViewSet):
    queryset = Breed.objects.select_related('species')
    serializer_class = BreedSerializer


class PetViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Pet.objects.select_related('owner__user', 'breed__species', 'medical_record')

    def get_serializer_class(self):
        if self.action in {'partial_update', 'update'}:
            return PetUpdateSerializer
        return PetSerializer

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if has_role(request.user, OWNER) and str(obj.owner_id) != str(request.user.id):
            raise PermissionDenied('No puedes acceder a mascotas de otro propietario.')
        if self.action in {'partial_update', 'update'} and not has_role(request.user, OWNER, VET):
            raise PermissionDenied('Solo el propietario o un veterinario pueden actualizar la mascota.')
        if self.action in {'vaccination_plan', 'vaccination_events'} and request.method == 'POST' and not has_role(request.user, VET):
            raise PermissionDenied('Solo veterinarios pueden crear planes o registrar vacunas.')

    def perform_destroy(self, instance):
        PetService.soft_delete(instance)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        pet = self.get_object()
        qs = pet.appointments.select_related('slot', 'vet__user__user', 'pet__breed__species').order_by('-scheduled_at')
        page = self.paginate_queryset(qs)
        serializer = AppointmentSerializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='medical-record')
    def medical_record(self, request, pk=None):
        pet = self.get_object()
        return Response(serialize_medical_record_for_pet(request, pet))

    @action(detail=True, methods=['get'], url_path='medical-record/summary')
    def medical_record_summary(self, request, pk=None):
        pet = self.get_object()
        return Response(serialize_medical_record_summary(pet))

    @action(detail=True, methods=['get'])
    def consultations(self, request, pk=None):
        pet = self.get_object()
        from apps.medical_records.serializers import ConsultationSerializer
        qs = pet.medical_record.consultations.select_related('vet__user__user', 'appointment').prefetch_related('treatments', 'prescriptions', 'attachments')
        return Response(ConsultationSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=True, methods=['get', 'post'], url_path='vaccination-plan')
    def vaccination_plan(self, request, pk=None):
        pet = self.get_object()
        if request.method == 'GET':
            plan = pet.vaccination_plans.filter(is_active=True).prefetch_related('items').first()
            if not plan:
                return Response({'detail': 'La mascota no tiene plan de vacunación activo.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(VaccinationPlanSerializer(plan).data)
        serializer = VaccinationPlanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = VaccinationService.create_plan(patient=pet, vet_user=request.user, data=serializer.validated_data)
        return Response(VaccinationPlanSerializer(plan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='vaccination-plan/schedule')
    def vaccination_schedule(self, request, pk=None):
        pet = self.get_object()
        return Response({'results': VaccinationService.schedule(patient=pet)})

    @action(detail=True, methods=['get', 'post'], url_path='vaccination-events')
    def vaccination_events(self, request, pk=None):
        pet = self.get_object()
        if request.method == 'GET':
            return Response(VaccinationEventSerializer(pet.vaccination_events.all().order_by('-applied_date'), many=True).data)
        serializer = VaccinationEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = VaccinationService.register_event(patient=pet, vet_user=request.user, data=serializer.validated_data)
        return Response(VaccinationEventSerializer(event).data, status=status.HTTP_201_CREATED)
