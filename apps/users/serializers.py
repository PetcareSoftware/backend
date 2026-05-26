from rest_framework import serializers
from .models import Supply, AuditLog  # Modelos actualizados a inglés
from django.contrib.auth import get_user_model, authenticate
import re

User = get_user_model()

class SupplySerializer(serializers.ModelSerializer):
    in_stock_alert = serializers.SerializerMethodField()

    class Meta:
        model = Supply
        # Definición de la información concreta usando los campos en inglés
        fields = [
            "id",
            "name",
            "current_stock",
            "minimum_threshold",
            "expiration_date",
            "is_active",
            "in_stock_alert",  # Metadato de control
        ]

        # Seguridad: El ID y el estado de alerta no deben ser modificables manualmente
        read_only_fields = ["id", "in_stock_alert"]

    def get_in_stock_alert(self, obj):
        """
        Lógica de monitoreo: Indica si el insumo cruzó el umbral mínimo.
        """
        return obj.current_stock <= obj.minimum_threshold

    def validate_current_stock(self, value):
        """
        Validación de seguridad: No permite registrar ingresos negativos.
        """
        if value < 0:
            raise serializers.ValidationError(
                "El stock no puede ser un número negativo."
            )
        return value

    def validate(self, data):
        """
        Validación de metadatos: Verifica que la fecha de vencimiento sea coherente.
        (Opcional: podrías validar que no se ingresen insumos ya vencidos)
        """
        # Aquí podrías añadir lógica extra de seguridad de datos
        return data


# 1. VALIDACIÓN PARA REGISTRO DE USUARIO
class UserRegistrationSerializer(serializers.ModelSerializer):
    # Escribimos write_only=True para que la contraseña nunca se devuelva al leer datos
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate_password(self, value):
        # Validamos las politicas de seguridad
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos un número.")
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos un carácter especial.")
            
        return value

    def create(self, validated_data):
        # Utilizamos create_user para que Django encripte la contraseña de forma segura
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


# 2. VALIDACIÓN PARA INICIO DE SESIÓN (LOGIN)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # authenticate revisa en la base de datos si el correo y la contraseña coinciden
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Las credenciales proporcionadas son incorrectas.", code='authorization')
        else:
            raise serializers.ValidationError("Debe incluir el correo y la contraseña.", code='authorization')

        # Si todo está bien, guardamos el usuario validado para usarlo después
        data['user'] = user
        return data


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True, default='Sistema')
    summary = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'path', 'timestamp', 'details', 'summary']
        read_only_fields = fields

    def get_summary(self, obj):
        usuario_str = obj.user.username if obj.user else 'Anónimo'
        return f"{obj.action} {obj.path} ({usuario_str})"