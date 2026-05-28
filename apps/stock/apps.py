from django.apps import AppConfig

class StockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.stock'

    def ready(self):
        # Preparado para la carga de señales del módulo de inventario
        pass
