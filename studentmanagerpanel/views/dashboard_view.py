
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students

def student_manager_dashboard(request):
    students_count = Students.objects.filter(deleted_at__isnull=True,student_manager_email=request.user.email ).count()
    data = {
        'students_count': students_count,
    }
    return render(request, "dashboard.html", data)
