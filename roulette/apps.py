from django.apps import AppConfig


class RouletteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'roulette'

    def ready(self):
        from . import signals  # Import signals module
        # from . import roulette  # Import signals module
