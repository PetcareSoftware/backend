from rest_framework import serializers
from apps.users.models import Veterinarian
from .models import TimeSlot, VetSchedule


class VetSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user_id', read_only=True)
    full_name = serializers.CharField(read_only=True)
    speciality = serializers.CharField(source='specialty', read_only=True)

    class Meta:
        model = Veterinarian
        fields = ['id', 'full_name', 'speciality', 'license_number', 'max_appts_per_day']


class VetScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetSchedule
        fields = ['id', 'vet_id', 'day_of_week', 'start_time', 'end_time', 'slot_duration_min', 'is_active']
        read_only_fields = ['id', 'vet_id']

    def validate(self, attrs):
        if attrs.get('start_time') and attrs.get('end_time') and attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError({'end_time': ['Debe ser posterior a start_time.']})
        return attrs


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'date', 'start_time', 'end_time', 'status']


class CalendarSerializer(serializers.Serializer):
    from_date = serializers.DateField(source='from')
    to = serializers.DateField()
    vets = serializers.ListField()
