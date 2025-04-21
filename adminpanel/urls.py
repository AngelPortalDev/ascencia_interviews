from django.urls import path
from django.urls import path, include
from adminpanel.views.profile_view import profile_update
from adminpanel.views.dashboard_view import admindashboard, custom_404_view
from adminpanel.views.institute_view import institute_list, institute_add, institute_update, institute_delete, toggle_institute_status, student_managers_by_institute
from adminpanel.views.course_view import courses, course_add, course_update, course_delete
from adminpanel.views.question_view import questions, question_add, question_update, question_delete, common_questions, common_question_add, common_question_update, common_question_delete
from adminpanel.views.student_manager_view import student_managers, student_manager_add, student_manager_update, student_manager_delete, toggle_student_manager_status, student_list_by_manager
from adminpanel.views.student_view import students_leads_api,students_list, student_detail



urlpatterns = [
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
                    path("institute/toggle-institute-status/<id>/", toggle_institute_status, name="toggle_institute_status"),
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
                    path("student_manager/toggle-student-manager-status/<id>/", toggle_student_manager_status, name="toggle_student_manager_status"),
                    path('student_manager/<str:id>/students/', student_list_by_manager, name='student_list_by_manager'),


                # student 
                    path("students/",students_list,name="students_list"),
                    path('student/<int:zoho_lead_id>/', student_detail, name='student_detail'),


                # Dashboards
                # path('dashboard/',userdashboard),
                path("dashboard/", admindashboard, name="admindashboard"),
            ]
        ),
    ),
]