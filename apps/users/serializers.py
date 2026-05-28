from django.contrib.auth import password_validation
from rest_framework import serializers

class UserPublicSerializer(serializers.Serializer):
    """Representación pública mínima de usuario para serializers de Backend 1.

    No consulta ni modifica modelos. Puede serializar tanto instancias reales
    de users.User como usuarios stateless construidos desde el JWT del Módulo 5.
    """

    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True, allow_blank=True)
    last_name = serializers.CharField(read_only=True, allow_blank=True)
    role = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    def to_representation(self, instance):
        role = getattr(instance, "role_name", None)
        if role is None:
            raw_role = getattr(instance, "role", "")
            role = getattr(raw_role, "name", raw_role)
        return {
            "id": str(getattr(instance, "id", "")),
            "email": getattr(instance, "email", ""),
            "first_name": getattr(instance, "first_name", ""),
            "last_name": getattr(instance, "last_name", ""),
            "role": role or "",
            "is_active": bool(getattr(instance, "is_active", True)),
        }


class AuthenticatedUserSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    def to_representation(self, instance):
        return {
            "id": str(getattr(instance, "id", "")),
            "email": getattr(instance, "email", ""),
            "role": getattr(instance, "role", getattr(instance, "role_name", "")),
            "is_active": bool(getattr(instance, "is_active", True)),
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    new_password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({
                "new_password_confirm": ["Las contraseñas no coinciden."]
            })
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": ["La nueva contraseña no puede ser igual a la anterior."]
            })

        # Backend 1 no valida old_password contra la base de datos: eso le
        # corresponde al Módulo 5. Aquí solo se aplican validadores de formato.
        password_validation.validate_password(attrs["new_password"])
        return attrs


class AuthRegisterProxySerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    dni = serializers.CharField(required=False, allow_blank=True, max_length=20)
    address = serializers.CharField(required=False, allow_blank=True)
    emergency_contact = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": ["Las contrasenas no coinciden."]
            })
        return attrs


class AuthLoginProxySerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class AuthRefreshProxySerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=False)


class AuthLogoutProxySerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=False)
