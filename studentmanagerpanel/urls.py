from django.urls import path
from django.urls import path, include
from studentmanagerpanel.views.dashboard_view import student_manager_dashboard


urlpatterns = [
    path(
        "studentmanagerpanel/",
        include(
            [
                # Dashboards
                path("dashboard/", student_manager_dashboard, name="studentmanagerdashboard"),
            ]
        ),
    ),
]
