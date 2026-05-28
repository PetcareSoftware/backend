from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from apps.common.roles import OWNER, has_role
from .models import Consultation, MedicalAttachment, MedicalRecord, Prescription, SupplyUsed, Treatment


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = ['id', 'name', 'description', 'start_date', 'duration_days', 'created_at']
        read_only_fields = ['id', 'created_at']


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'medicine_name', 'dosage', 'frequency', 'duration_days', 'supply_id', 'instructions', 'created_at']
        read_only_fields = ['id', 'created_at']


class MedicalAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    type = serializers.CharField(source='attachment_type', read_only=True)

    class Meta:
        model = MedicalAttachment
        fields = ['id', 'attachment_type', 'type', 'file', 'url', 'description', 'uploaded_at']
        read_only_fields = ['id', 'url', 'uploaded_at']

    def get_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def validate_file(self, value):
        allowed_content_types = {'application/pdf', 'image/jpeg', 'image/png'}
        allowed_ext = ('.pdf', '.jpg', '.jpeg', '.png')
        content_type = getattr(value, 'content_type', '')
        name = getattr(value, 'name', '').lower()
        if content_type and content_type not in allowed_content_types:
            raise serializers.ValidationError('Solo se permiten archivos PDF, JPG y PNG.')
        if not name.endswith(allowed_ext):
            raise serializers.ValidationError('Solo se permiten archivos PDF, JPG y PNG.')
        if getattr(value, 'size', 0) > 10 * 1024 * 1024:
            raise serializers.ValidationError('El tamaño máximo por archivo es 10 MB.')
        return value


class SupplyUsedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyUsed
        fields = ['id', 'supply_id', 'supply_name', 'quantity', 'unit_cost', 'sync_status', 'created_at']
        read_only_fields = ['id', 'supply_name', 'unit_cost', 'sync_status', 'created_at']




class SupplyUsedInputSerializer(serializers.Serializer):
    supply_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))


class SuppliesUsedRequestSerializer(serializers.Serializer):
    supplies = SupplyUsedInputSerializer(many=True, allow_empty=False)


class ConsultationSerializer(serializers.ModelSerializer):
    treatments = TreatmentSerializer(many=True, read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    attachments = MedicalAttachmentSerializer(many=True, read_only=True)
    supplies_used = SupplyUsedSerializer(many=True, read_only=True)
    appointment_status = serializers.CharField(source='appointment.status', read_only=True)
    vet = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = ['id', 'medical_record_id', 'appointment_id', 'vet_id', 'vet', 'diagnosis', 'clinical_notes', 'date', 'created_at', 'updated_at', 'treatments', 'prescriptions', 'attachments', 'supplies_used', 'appointment_status']
        read_only_fields = ['id', 'medical_record_id', 'vet_id', 'date', 'created_at', 'updated_at', 'appointment_status']

    def get_vet(self, obj):
        return obj.vet.full_name if obj.vet_id else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and has_role(request.user, OWNER):
            data['clinical_notes'] = None
        return data


class ConsultationCreateSerializer(serializers.Serializer):
    diagnosis = serializers.CharField(max_length=500)
    clinical_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    treatments = TreatmentSerializer(many=True, required=False)
    prescriptions = PrescriptionSerializer(many=True, required=False)


class ConsultationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ['diagnosis', 'clinical_notes']

    def validate(self, attrs):
        consultation = self.instance
        if consultation and timezone.now() - consultation.created_at > timedelta(hours=24):
            raise PermissionDenied('La consulta solo puede editarse dentro de las primeras 24 horas.')
        return attrs


class MedicalRecordSerializer(serializers.ModelSerializer):
    pet = serializers.SerializerMethodField()
    consultations = ConsultationSerializer(many=True, read_only=True)
    vaccination_plan = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = ['id', 'pet', 'consultations', 'vaccination_plan', 'created_at']

    def get_pet(self, obj):
        pet = obj.patient
        return {'id': str(pet.id), 'name': pet.name, 'species': pet.breed.species.name if pet.breed_id else None, 'breed': pet.breed.name if pet.breed_id else None}

    def get_vaccination_plan(self, obj):
        plan = obj.patient.vaccination_plans.filter(is_active=True).first()
        return {'id': str(plan.id), 'is_active': plan.is_active} if plan else None


class MedicalRecordSummarySerializer(serializers.Serializer):
    pet = serializers.DictField()
    last_consultation = serializers.DictField(allow_null=True)
    active_treatments = serializers.ListField()
    vaccination_status = serializers.CharField()
    next_vaccine_due = serializers.DateField(allow_null=True)
    total_consultations = serializers.IntegerField()
