from rest_framework import serializers
from .models import Insumo, LogEntry
from django.contrib.auth import get_user_model, authenticate
import re

User = get_user_model()

# ---------- Serializadores existentes ----------
class InsumoSerializer(serializers.ModelSerializer):
    en_alerta_stock = serializers.SerializerMethodField()

    class Meta:
        model = Insumo
        fields = [
            "id",
            "nombre",
            "stock_actual",
            "umbral_minimo",
            "fecha_vencimiento",
            "esta_activo",
            "en_alerta_stock",
        ]
        read_only_fields = ["id", "en_alerta_stock"]

    def get_en_alerta_stock(self, obj):
        return obj.stock_actual <= obj.umbral_minimo

    def validate_stock_actual(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser un número negativo.")
        return value

    def validate(self, data):
        return data


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos un número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos un carácter especial.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Las credenciales proporcionadas son incorrectas.", code='authorization')
        else:
            raise serializers.ValidationError("Debe incluir el correo y la contraseña.", code='authorization')
        data['user'] = user
        return data


# ---------- NUEVO: Serializador para Logs ----------
class LogEntrySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = LogEntry
        fields = [
            'id',
            'timestamp',
            'user',
            'user_email',
            'action',
            'details',
            'ip_address',
        ]
        read_only_fields = fields