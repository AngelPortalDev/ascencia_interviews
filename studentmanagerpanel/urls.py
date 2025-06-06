from django.urls import path
from django.urls import path, include
from studentmanagerpanel.views.dashboard_view import student_manager_dashboard
from studentmanagerpanel.views.profile_view import profile_update
from studentmanagerpanel.views.student_view import students_list, student_detail


urlpatterns = [
    path(
        "studentmanagerpanel/",
        include(
            [
                # Dashboards
                path("dashboard/", student_manager_dashboard, name="studentmanagerdashboard"),
                
                # profile
                    path('profile-update/', profile_update, name='studentmanager_profile_update'),

                # Students
                path("students/", students_list, name="studentmanager_students_list"),
                path('student/<int:zoho_lead_id>/', student_detail, name='studentmanager_student_detail'),
            ]
        ),
    ),
]
