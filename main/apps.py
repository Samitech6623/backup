from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        """Imports the signals module to register the handlers."""
        # 🔑 FIX: Import your signals file here. 
        # Assuming your signal logic is in 'main/signals.py'.
        import main.signals