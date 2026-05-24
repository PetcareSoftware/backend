from rest_framework import serializers

from owners.models import Owner
from patients.models import Pet
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura para los datos del usuario embebidos en el perfil del propietario."""

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = fields


class OwnerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para el perfil completo del propietario.
    Incluye los datos del User anidado.
    Usado en: GET /owners/me/  y  GET /owners/{id}/  y  GET /owners/
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Owner
        fields = ('id', 'user', 'phone', 'address', 'created_at')
        read_only_fields = fields


class OwnerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización parcial del perfil del propietario.
    Permite editar campos propios (phone, address) y campos del User (first_name, last_name).
    Usado en: PATCH /owners/me/
    """

    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'phone', 'address')

    def update(self, instance, validated_data):
        # Extraer datos anidados del User antes de actualizar Owner
        user_data = validated_data.pop('user', {})

        # Actualizar campos del Owner
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar campos del User si se enviaron
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance


class PetSerializer(serializers.ModelSerializer):
    """
    Serializer para listar y crear mascotas.
    El campo owner es de solo lectura (se asigna automáticamente en perform_create).
    Usado en: GET /owners/me/pets/  y  POST /owners/me/pets/
    """

    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Pet
        fields = (
            'id',
            'owner_id',
            'name',
            'species',
            'breed',
            'date_of_birth',
            'sex',
            'weight_kg',
            'created_at',
        )
        read_only_fields = ('id', 'owner_id', 'created_at')
