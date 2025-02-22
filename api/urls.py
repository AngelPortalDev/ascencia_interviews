from django.urls import path
from .views import process_document, fetch_interview_questions

urlpatterns = [
    path('process_document', process_document, name='process_document'),
    path('fetch_interview_questions', fetch_interview_questions, name='fetch_interview_questions'),
]
