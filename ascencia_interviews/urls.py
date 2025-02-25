from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, include
from adminpanel.views.auth_view import login_view, register_view, logout_view, index
from adminpanel.views.dashboard_view import admindashboard, custom_404_view
from adminpanel.views.institute_view import institute_list, institute_add, institute_update, institute_delete, student_managers_by_institute
from adminpanel.views.course_view import courses, course_add, course_update, course_delete
from adminpanel.views.question_view import questions, question_add, question_update, question_delete, common_questions, common_question_add, common_question_update, common_question_delete
from adminpanel.views.student_manager_view import student_managers, student_manager_add, student_manager_update, student_manager_delete, student_list_by_manager
from adminpanel.views.profile_view import profile_update
from adminpanel.views.student_view import students_leads_api,students_list, student_detail
from django.views.generic import TemplateView
from django.conf.urls import handler404
from django.shortcuts import redirect
from studentpanel.views.interview_analyze import analyze_video,check_answers

handler404 = custom_404_view

# studentpanel settings
from studentpanel.views.interview_process import (
    interview_start,
    interview_panel,
    interview_score,
    interview_video_upload,
    interview_questions
)

# interview_panel,
# interview_score


def redirect_to_dashboard(request):
    return redirect('/adminpanel/dashboard')

urlpatterns = [
    path('', redirect_to_dashboard),
    path("index/", index),
    path("admin/", admin.site.urls),
    path("api/", include('api.urls')),
    path("", include('studentmanagerpanel.urls')),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path(
        "adminpanel/",
        include(
            [
                # profile
                    path('profile-update/', profile_update, name='profile_update'),

                # institute
                    path("institute/", institute_list, name="institute_list"),
                    path("institute/add", institute_add, name="institute_add"),
                    path("institute/update/<id>/", institute_update, name="institute_update"),
                    path("institute/delete/<id>/", institute_delete, name="institute_delete"),
                    path('institute/<str:id>/student-managers/', student_managers_by_institute, name='student_managers_by_institute'),


                # courses
                    path("courses/", courses, name="courses"),
                    path("course/add", course_add, name="course_add"),
                    path("course/update/<id>/", course_update, name="course_update"),
                    path("course/delete/<id>/", course_delete, name="course_delete"),

                # common questions
                    path("common_questions/", common_questions, name="common_questions"),
                    path("common_question/add", common_question_add, name="common_question_add"),
                    path("common_question/update/<id>/", common_question_update, name="common_question_update"),
                    path("common_question/delete/<id>/", common_question_delete, name="common_question_delete"),

                # questions
                    path("questions/", questions, name="questions"),
                    path("question/add", question_add, name="question_add"),
                    path("question/update/<id>/", question_update, name="question_update"),
                    path("question/delete/<id>/", question_delete, name="question_delete"),
                    
                # student managers
                    path("student_managers/", student_managers, name="student_managers"),
                    path("student_manager/add", student_manager_add, name="student_manager_add"),
                    path("student_manager/update/<id>/", student_manager_update, name="student_manager_update"),
                    path("student_manager/delete/<id>/", student_manager_delete, name="student_manager_delete"),
                    path('student_manager/<str:id>/students/', student_list_by_manager, name='student_list_by_manager'),


                # student 
                    path('student/<int:zoho_lead_id>/', student_detail, name='student_detail'),


                # Dashboards
                # path('dashboard/',userdashboard),
                path("dashboard/", admindashboard, name="admindashboard"),
                path("students/",students_list,name="students_list")
            ]
        ),
    ),
    path('students_leads_api/', students_leads_api, name='students_leads_api'),

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
                path("check-answers/", check_answers, name="check_answers")
                # path("index/", index, name="index"),
            ]
        ),
    ),
    path('home', TemplateView.as_view(template_name='index.html')),
    path('terms-and-conditions', TemplateView.as_view(template_name='index.html')),
    path('permissions', TemplateView.as_view(template_name='index.html')),
    path('interview-player', TemplateView.as_view(template_name='index.html')),    
]
