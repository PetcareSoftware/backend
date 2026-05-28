from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from apps.common.permissions import IsOwner, IsReceptionist, IsSelfOwnerOrReceptionist
from apps.appointments.serializers import AppointmentSerializer
from apps.pets.serializers import PetCreateSerializer, PetSerializer
from apps.pets.services import PetService
from .models import Owner
from .serializers import OwnerListSerializer, OwnerSerializer, OwnerUpdateSerializer


class OwnerViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'user_id'
    queryset = Owner.objects.select_related('user').prefetch_related('pets__breed__species')

    def get_serializer_class(self):
        if self.action == 'list':
            return OwnerListSerializer
        if self.action == 'update_me':
            return OwnerUpdateSerializer
        return OwnerSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsReceptionist()]
        if self.action in {'me', 'update_me', 'my_pets', 'my_appointments'}:
            return [IsOwner()]
        return [IsSelfOwnerOrReceptionist()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            name = self.request.query_params.get('name') or self.request.query_params.get('search')
            dni = self.request.query_params.get('dni')
            if name:
                qs = qs.filter(user__first_name__icontains=name) | qs.filter(user__last_name__icontains=name)
            if dni:
                qs = qs.filter(dni__icontains=dni)
        return qs.order_by('user__last_name', 'user__first_name')

    def _my_owner(self):
        try:
            return Owner.objects.select_related('user').prefetch_related('pets__breed__species').get(user_id=self.request.user.id)
        except Owner.DoesNotExist as exc:
            raise NotFound('El propietario autenticado no tiene perfil Owner asociado.') from exc

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        return Response(OwnerSerializer(self._my_owner(), context={'request': request}).data)

    @me.mapping.patch
    def update_me(self, request):
        owner = self._my_owner()
        serializer = OwnerUpdateSerializer(owner, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'], url_path='me/pets')
    def my_pets(self, request):
        owner = self._my_owner()
        if request.method == 'GET':
            pets = owner.pets.select_related('breed__species').order_by('name')
            return Response(PetSerializer(pets, many=True).data)
        serializer = PetCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        pet = PetService.create_pet_for_owner(owner=owner, data=serializer.validated_data)
        return Response(PetSerializer(pet).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='me/appointments')
    def my_appointments(self, request):
        owner = self._my_owner()
        qs = owner.pets_appointments().select_related('pet__breed__species', 'vet__user__user', 'slot')
        page = self.paginate_queryset(qs)
        serializer = AppointmentSerializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
