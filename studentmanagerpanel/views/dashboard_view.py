
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from studentpanel.models.interview_link import StudentInterviewLink
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Exists

def student_manager_dashboard(request):
    students_count = Students.objects.filter(deleted_at__isnull=True, student_manager_email=request.user.email ).count()
    
    verified_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='approved', student_manager_email=request.user.email ).count() or 0
    rejected_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='rejected', student_manager_email=request.user.email ).count() or 0
    
    valid_students = Students.objects.filter(
        deleted_at__isnull=True,
        student_manager_email=request.user.email,
        zoho_lead_id=OuterRef('zoho_lead_id')
    )

    # Pending Interviews Count
    pending_interviews_count = StudentInterviewLink.objects.filter(
        expires_at__gt=timezone.now(),
        is_expired=0,
        zoho_lead_id__in=Subquery(valid_students.values("zoho_lead_id"))
    ).count() or 0

    # Passed Students Count
    pass_students_count = StudentInterviewLink.objects.filter(
        interview_status='Pass',
        zoho_lead_id__in=Subquery(valid_students.values("zoho_lead_id"))
    ).count() or 0

    # Failed Students Count
    fail_students_count = StudentInterviewLink.objects.filter(
        interview_status='Fail',
        zoho_lead_id__in=Subquery(valid_students.values("zoho_lead_id"))
    ).count() or 0

    students = Students.objects.filter(
        deleted_at__isnull=True, 
        edu_doc_verification_status='approved',
        student_manager_email=request.user.email 
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
    return render(request, "dashboard.html", data)
