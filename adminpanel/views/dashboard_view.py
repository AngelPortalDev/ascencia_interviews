
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from studentpanel.models.interview_link import StudentInterviewLink
from django.utils import timezone


def admindashboard(request):

    students_count = Students.objects.filter(deleted_at__isnull=True).count()
    verified_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='approved').count() or 0
    rejected_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='rejected').count() or 0
    
    pending_interviews_count = StudentInterviewLink.objects.filter(
        expires_at__gt=timezone.now(), 
        is_expired=0
    ).count() or 0
    
    pass_students_count = StudentInterviewLink.objects.filter(
        interview_status='Pass'
    ).count() or 0

    fail_students_count = StudentInterviewLink.objects.filter(
        interview_status='Fail'
    ).count() or 0

    
    students = Students.objects.filter(
        deleted_at__isnull=True, 
        edu_doc_verification_status='approved'
    ).order_by('-id')[:4]
    
    students_with_interview_status = []
    for student in students:
        interview_status = StudentInterviewLink.objects.filter(zoho_lead_id=student.zoho_lead_id).first()
        students_with_interview_status.append({
            'student': student,
            'interview_status': interview_status.interview_status if interview_status else 'Not Available'
        })


    data = {
        'students_count': students_count,
        'verified_students_count': verified_students_count,
        'rejected_students_count': rejected_students_count,
        'pending_interviews_count': pending_interviews_count,
        'pass_students_count': pass_students_count,
        'fail_students_count': fail_students_count,
        'students_with_interview_status': students_with_interview_status,
    }
    return render(request, "admindashboard.html", data)

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)