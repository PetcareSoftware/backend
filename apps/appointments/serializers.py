from rest_framework import serializers
from apps.pets.serializers import PetSerializer
from apps.schedules.serializers import TimeSlotSerializer, VetSerializer
from .models import Appointment, WaitingListEntry


class AppointmentSerializer(serializers.ModelSerializer):
    pet = PetSerializer(read_only=True)
    vet = VetSerializer(read_only=True)
    slot = TimeSlotSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'pet', 'vet', 'slot', 'reason', 'status', 'notes', 'scheduled_at', 'cancelled_at', 'cancellation_reason', 'created_at']


class AppointmentCreateSerializer(serializers.Serializer):
    pet_id = serializers.UUIDField()
    vet_id = serializers.UUIDField()
    slot_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=500)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AppointmentUpdateSerializer(serializers.Serializer):
    slot_id = serializers.UUIDField(required=False)
    reason = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AppointmentCancelSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class WaitingListSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = WaitingListEntry
        fields = ['id', 'appointment', 'position', 'arrived_at', 'called_at']
