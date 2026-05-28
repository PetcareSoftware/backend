from rest_framework import serializers
from .models import Breed, Pet, Species


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name']


class BreedSerializer(serializers.ModelSerializer):
    species = SpeciesSerializer(read_only=True)
    species_id = serializers.PrimaryKeyRelatedField(source='species', queryset=Species.objects.all(), write_only=True)

    class Meta:
        model = Breed
        fields = ['id', 'name', 'species', 'species_id']


class PetSerializer(serializers.ModelSerializer):
    owner_id = serializers.UUIDField(source='owner.user_id', read_only=True)
    breed = BreedSerializer(read_only=True)
    medical_record_id = serializers.UUIDField(source='medical_record.id', read_only=True)

    class Meta:
        model = Pet
        fields = ['id', 'owner_id', 'name', 'breed', 'birth_date', 'sex', 'weight_kg', 'color', 'microchip_id', 'medical_record_id', 'created_at']
        read_only_fields = ['id', 'owner_id', 'breed', 'medical_record_id', 'created_at']


class PetCreateSerializer(serializers.ModelSerializer):
    breed_id = serializers.PrimaryKeyRelatedField(source='breed', queryset=Breed.objects.all())

    class Meta:
        model = Pet
        fields = ['name', 'breed_id', 'birth_date', 'sex', 'weight_kg', 'color', 'microchip_id']


class PetUpdateSerializer(serializers.ModelSerializer):
    breed_id = serializers.PrimaryKeyRelatedField(source='breed', queryset=Breed.objects.all(), required=False)

    class Meta:
        model = Pet
        fields = ['name', 'breed_id', 'birth_date', 'sex', 'weight_kg', 'color', 'microchip_id']

    def to_representation(self, instance):
        return PetSerializer(instance).data
