from django.urls import path
from django.urls import path, include

# studentpanel settings
from studentpanel.views.interview_process import (
    interview_start,
    interview_panel,
    interview_score,
    interview_video_upload,
    interview_questions,
    student_data
)
from studentpanel.views.interview_analyze import analyze_video,check_answers
from django.views.generic import TemplateView


urlpatterns = [
    # Interview Section URLS
    path(
        "interveiw-section/",
        include(
            [
                path(
                    "interview-instructions/",
                    interview_start,
                    name="interview-instructions",
                ),
                path("interview-panel/", interview_panel, name="interview_panel"),
                # path("answer-question/", student_answer, name="student_answer"),
                # path("upload-recording/", student_upload, name="student_upload"),
                # path("submit-interview/", student_submit, name="student_submit"),
                path("interview-score/", interview_score, name="interview_score"),
                path("interview-video-upload/", interview_video_upload, name="interview_video_upload"),
                path("interview-questions/", interview_questions, name="interview_questions"),
                path("analyze-video/", analyze_video, name="analyze_video"),
                path("check-answers/", check_answers, name="check_answers"),
                path("student-data/", student_data, name="student_data")

                # path("index/", index, name="index"),
            ]
        ),
    ),

    # path('interview_panel/<str:student_id>/', TemplateView.as_view(template_name='index.html')),
    # path('terms-and-conditions/', TemplateView.as_view(template_name='index.html')),
    # path('permissions/', TemplateView.as_view(template_name='index.html')),
    # path('interview-player/<str:student_id>/', TemplateView.as_view(template_name='index.html')),    
]
