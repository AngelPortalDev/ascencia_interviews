
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students

def admindashboard(request):

    students_count = Students.objects.filter(deleted_at__isnull=True).count()
    data = {
        'students_count': students_count,
    }
    return render(request, "admindashboard.html", data)

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)