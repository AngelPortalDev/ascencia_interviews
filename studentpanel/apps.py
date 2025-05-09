from django.apps import AppConfig


class StudentpanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studentpanel'
    verbose_name = 'Student Panel'  # Optional: A human-readable name for the app

    def ready(self):    
        import studentpanel.observer.video_merge_handler  # Ensures signals are registered
 
