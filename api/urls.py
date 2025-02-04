from django.urls import path
from .views import process_lead

urlpatterns = [
    path('process-lead/', process_lead, name='process-lead'),
]
