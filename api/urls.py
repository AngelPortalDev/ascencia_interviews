from django.urls import path
from .views import process_document

urlpatterns = [
    path('process_document', process_document, name='process_document'),
]
