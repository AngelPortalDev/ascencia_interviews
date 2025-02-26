from django.urls import path
from django.urls import path, include
from studentmanagerpanel.views.dashboard_view import student_manager_dashboard
from studentmanagerpanel.views.student_view import students_list


urlpatterns = [
    path(
        "studentmanagerpanel/",
        include(
            [
                # Dashboards
                path("dashboard/", student_manager_dashboard, name="studentmanagerdashboard"),

                # Students
                path("students/", students_list, name="studentmanager_students_list")
            ]
        ),
    ),
]
