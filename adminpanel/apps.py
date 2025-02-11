from django.apps import AppConfig


class AdminpanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminpanel'

    def ready(self):
        import adminpanel.observer.document_check_observer  # Ensures signals are registered when the app starts

 
