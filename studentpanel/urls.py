from django.urls import path
from django.urls import path, include
from studentpanel.views.interview_submit import submit_interview

# studentpanel settings
from studentpanel.views.interview_process import (
    interview_attend,
    # interview_panel,
    # interview_score,
    interview_video_upload,
    interview_questions,
    student_data
    
)
from studentpanel.views.interview_analyze import analyze_video,check_answers, merge_videos, delete_video,interview_add_video_path,student_interview_answers
from django.views.generic import TemplateView


urlpatterns = [
    # Interview Section URLS
    path(
        "interveiw-section/",
        include(
            [
                path(
                    "interview-attend-status/",
                    interview_attend,
                    name="interview-attend-status",
                ),
                # path("interview-panel/", interview_panel, name="interview_panel"),
                # path("answer-question/", student_answer, name="student_answer"),
                # path("upload-recording/", student_upload, name="student_upload"),
                # path("submit-interview/", student_submit, name="student_submit"),
                # path("interview-score/", interview_score, name="interview_score"),
                path("interview-video-upload/", interview_video_upload, name="interview_video_upload"),
                path("interview-questions/", interview_questions, name="interview_questions"),
                path("analyze-video/", analyze_video, name="analyze_video"),
                path("check-answers/", check_answers, name="check_answers"),
                path("student-data/", student_data, name="student_data"),
                path("student-interview-answers/", student_interview_answers, name="student_interview_answers"),
                path("interview-add-video-path/", interview_add_video_path, name="interview_add_video_path"),

                
                # path("index/", index, name="index"),
            ]
        ),
    ),
    path("delete-video/<int:student_id>/", delete_video, name="delete_video"),
    # path('merge-videos/', merge_videos, name='merge_videos'),
    path('interview_panel/<str:student_id>/', TemplateView.as_view(template_name='index.html')),
    path('terms-and-conditions/', TemplateView.as_view(template_name='index.html')),
    path('permissions/', TemplateView.as_view(template_name='index.html')),
    path('interview-player/<str:student_id>/', TemplateView.as_view(template_name='index.html')),  
    path("submit_interview/", submit_interview, name="submit_interview"),
]
