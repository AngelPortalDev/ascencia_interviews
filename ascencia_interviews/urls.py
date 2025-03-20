from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path,re_path, include
from adminpanel.views.auth_view import login_view, register_view, logout_view, index
from adminpanel.views.dashboard_view import admindashboard, custom_404_view
from adminpanel.views.institute_view import institute_list, institute_add, institute_update, institute_delete, student_managers_by_institute
from adminpanel.views.course_view import courses, course_add, course_update, course_delete
from adminpanel.views.question_view import questions, question_add, question_update, question_delete, common_questions, common_question_add, common_question_update, common_question_delete
from adminpanel.views.student_manager_view import student_managers, student_manager_add, student_manager_update, student_manager_delete, student_list_by_manager
from adminpanel.views.profile_view import profile_update
from adminpanel.views.student_view import students_leads_api,students_list, student_detail
from django.conf.urls import handler404
from django.shortcuts import redirect

handler404 = custom_404_view


# interview_panel,
# interview_score


def redirect_to_dashboard(request):
    
    return redirect('/adminpanel/dashboard')

urlpatterns = [
    # path('', redirect_to_dashboard),
    path("", login_view, name="login"),
    path("index/", index),
    path("admin/", admin.site.urls),
    path("api/", include('api.urls')),
    path("login", login_view, name="login"),
    path("register", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("", include('adminpanel.urls')),
    path("", include('studentpanel.urls')),
    path("", include('studentmanagerpanel.urls')),

    # ✅ Serve React frontend only for non-backend paths
    re_path(r'^(?!api/|admin/|login|logout|register).*$', index),
 

    # Interview Section URLS

    # path(
    #     "interveiw-section/",
    #     include(
    #         [
    #             path(
    #                 "interview-instructions/",
    #                 interview_start,
    #                 name="interview-instructions",
    #             ),
    #             path("interview-panel/", interview_panel, name="interview_panel"),
    #             # path("answer-question/", student_answer, name="student_answer"),
    #             # path("upload-recording/", student_upload, name="student_upload"),
    #             # path("submit-interview/", student_submit, name="student_submit"),
    #             path("interview-score/", interview_score, name="interview_score"),
    #             path("interview-video-upload/", interview_video_upload, name="interview_video_upload"),
    #             path("interview-questions/", interview_questions, name="interview_questions"),
    #             path("analyze-video/", analyze_video, name="analyze_video"),
    #             path("check-answers/", check_answers, name="check_answers"),
    #             path("student-data/", student_data, name="student_data")

    #             # path("index/", index, name="index"),
    #         ]
    #     ),
    # ),
  
]
