from django_tasks import task
from .models import Supply  # Importamos el modelo en inglés
from django.db.models import F

@task
def check_stock_alerts():
    # Busca insumos donde el stock es menor o igual al umbral
    supplies_on_alert = Supply.objects.filter(current_stock__lte=F("minimum_threshold"))
    
    for supply in supplies_on_alert:
        print(f"ALERTA DE SEGURIDAD: Insumo {supply.name} está agotándose.")
        # Aquí podrías enviar un correo o crear una notificación en DB