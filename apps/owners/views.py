from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from owners.models import Owner
from owners.permissions import IsOwner, IsReceptionist
from owners.serializers import OwnerProfileSerializer, OwnerUpdateSerializer, PetSerializer
from patients.models import MedicalRecord, Pet


class OwnerMeView(generics.GenericAPIView):
    """
    GET  /api/v1/owners/me/ — Ver el perfil del propietario autenticado.
    PATCH /api/v1/owners/me/ — Editar los datos del perfil del propietario autenticado.

    Acceso: Solo propietarios autenticados (rol OWNER).
    Optimización: select_related('user') en el queryset.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        return Owner.objects.select_related('user').get(user=self.request.user)

    def get(self, request, *args, **kwargs):
        owner = self.get_object()
        serializer = OwnerProfileSerializer(owner)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        owner = self.get_object()
        serializer = OwnerUpdateSerializer(owner, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Retornar el perfil completo actualizado
        return Response(OwnerProfileSerializer(owner).data)


class OwnerListView(generics.ListAPIView):
    """
    GET /api/v1/owners/ — Listar todos los propietarios del sistema.

    Acceso: Exclusivo para RECEPTIONIST.
    Optimización: select_related('user') obligatorio para evitar N+1.
    """

    permission_classes = [IsAuthenticated, IsReceptionist]
    serializer_class = OwnerProfileSerializer

    def get_queryset(self):
        return Owner.objects.select_related('user').all()


class OwnerDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/owners/{id}/ — Ver el perfil de un propietario por su ID.

    Acceso: Exclusivo para RECEPTIONIST.
    Optimización: select_related('user') obligatorio para evitar N+1.
    """

    permission_classes = [IsAuthenticated, IsReceptionist]
    serializer_class = OwnerProfileSerializer

    def get_queryset(self):
        return Owner.objects.select_related('user').all()


class OwnerMePetsView(generics.GenericAPIView):
    """
    GET  /api/v1/owners/me/pets/ — Listar las mascotas del propietario autenticado (excluye soft-deleted).
    POST /api/v1/owners/me/pets/ — Registrar una nueva mascota para el propietario autenticado.

    Acceso: Solo propietarios autenticados (rol OWNER).
    POST: Envuelto en @transaction.atomic. Crea automáticamente un MedicalRecord vacío.
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = PetSerializer

    def get_owner(self):
        return self.request.user.owner

    def get(self, request, *args, **kwargs):
        owner = self.get_owner()
        # Filtro de soft delete: excluir mascotas con is_deleted=True
        pets = Pet.objects.filter(owner=owner, is_deleted=False)
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        owner = self.get_owner()
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Asignar el owner automáticamente desde el usuario en sesión
        pet = serializer.save(owner=owner)

        # Crear expediente clínico vacío asociado a la mascota
        MedicalRecord.objects.create(pet=pet)

        return Response(PetSerializer(pet).data, status=status.HTTP_201_CREATED)
