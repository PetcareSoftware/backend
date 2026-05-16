from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
import re

# Obtenemos el modelo de usuario que usa el proyecto
User = get_user_model()

# 1. VALIDACIÓN PARA REGISTRO DE USUARIO
class RegistroUsuarioSerializer(serializers.ModelSerializer):
    # Escribimos write_only=True para que la contraseña nunca se devuelva al leer datos
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate_password(self, value):
        #Validamos las politicas de seguridad
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