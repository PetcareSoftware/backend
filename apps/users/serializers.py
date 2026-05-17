from rest_framework import serializers
from .models import Insumo

class InsumoSerializer(serializers.ModelSerializer):
    en_alerta_stock = serializers.SerializerMethodField()

    class Meta:
        model = Insumo
        # Definición de la información concreta
        fields = [
            'id', 
            'nombre', 
            'stock_actual', 
            'umbral_minimo', 
            'fecha_vencimiento', 
            'esta_activo',
            'en_alerta_stock'  # Metadato de control
        ]
        
        # Seguridad: El ID y el estado de alerta no deben ser modificables manualmente
        read_only_fields = ['id', 'en_alerta_stock']

    def get_en_alerta_stock(self, obj):
        """
        Lógica de monitoreo: Indica si el insumo cruzó el umbral mínimo.
        """
        return obj.stock_actual <= obj.umbral_minimo

    def validate_stock_actual(self, value):
        """
        Validación de seguridad: No permite registrar ingresos negativos.
        """
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser un número negativo.")
        return value

    def validate(self, data):
        """
        Validación de metadatos: Verifica que la fecha de vencimiento sea coherente.
        (Opcional: podrías validar que no se ingresen insumos ya vencidos)
        """
        # Aquí podrías añadir lógica extra de seguridad de datos
        return data