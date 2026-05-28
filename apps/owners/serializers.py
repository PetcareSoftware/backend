from rest_framework import serializers
from apps.users.serializers import UserPublicSerializer
from .models import Owner


class OwnerPetSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    species = serializers.CharField(source='breed.species.name', allow_null=True)
    breed = serializers.CharField(source='breed.name', allow_null=True)
    sex = serializers.CharField()
    birth_date = serializers.DateField()


class OwnerSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user_id', read_only=True)
    user = UserPublicSerializer(read_only=True)
    pets = serializers.SerializerMethodField()

    class Meta:
        model = Owner
        fields = ['id', 'user', 'phone', 'address', 'dni', 'emergency_contact', 'pets']
        read_only_fields = ['id', 'user', 'dni', 'pets']

    def get_pets(self, obj):
        qs = obj.pets.filter(is_deleted=False).select_related('breed__species')
        return OwnerPetSummarySerializer(qs, many=True).data


class OwnerUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False, max_length=100)
    last_name = serializers.CharField(source='user.last_name', required=False, max_length=100)

    class Meta:
        model = Owner
        fields = ['first_name', 'last_name', 'phone', 'address', 'emergency_contact']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        if user_data:
            instance.user.save(update_fields=list(user_data.keys()) + ['updated_at'])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return OwnerSerializer(instance, context=self.context).data


class OwnerListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user_id', read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Owner
        fields = ['id', 'full_name', 'email', 'dni', 'phone']

    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'.strip()
