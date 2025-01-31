from django.urls import path
from .views import process_lead

urlpatterns = [
    path('process_lead/', process_lead, name='process_lead'),
]
