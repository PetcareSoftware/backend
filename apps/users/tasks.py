from django_tasks import task
from .models import Insumo

@task
def verificar_alertas_stock():
    # Busca insumos donde el stock es menor o igual al umbral
    insumos_en_alerta = Insumo.objects.filter(stock_actual__lte=F('umbral_minimo'))
    for insumo in insumos_en_alerta:
        print(f"ALERTA DE SEGURIDAD: Insumo {insumo.nombre} está agotándose.")
        # Aquí podrías enviar un correo o crear una notificación en DB