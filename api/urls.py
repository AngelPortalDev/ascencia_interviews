from django.urls import path
from .views import process_document, fetch_interview_questions,interview_create,get_daily_token

urlpatterns = [
    path('process_document', process_document, name='process_document'),
    path('fetch_interview_questions/<crm_id>/', fetch_interview_questions, name='fetch_interview_questions'),
    path('create_interview/', interview_create, name='interview_create'),
     path("daily/token/", get_daily_token, name="get_daily_token"),

]
