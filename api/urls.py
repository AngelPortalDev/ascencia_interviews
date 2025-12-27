from django.urls import path
from .dailyurls import urlpatterns as dailyurls
from .views import (
    process_document,
    fetch_interview_questions,
    interview_create,
    # get_daily_token,
    # start_daily_recording,
    # stop_daily_recording
)

urlpatterns = [
    path('process_document', process_document, name='process_document'),
    path('fetch_interview_questions/<crm_id>/', fetch_interview_questions, name='fetch_interview_questions'),
    path('create_interview/', interview_create, name='interview_create'),
 
     *dailyurls,
]
