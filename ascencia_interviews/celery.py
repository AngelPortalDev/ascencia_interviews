
# mysite/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ascencia_interviews.settings")

app = Celery("ascencia_interviews")

# Load config from Django settings (CELERY_... keys)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # will find tasks.py in installed apps
