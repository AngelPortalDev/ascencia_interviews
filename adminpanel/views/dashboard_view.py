
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from studentpanel.models.interview_link import StudentInterviewLink
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Exists, OuterRef

def admindashboard(request):

    students_count = Students.objects.filter(deleted_at__isnull=True).count()
    # verified_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='approved').count() or 0
    verified_students_count = Students.objects.annotate(
            interview_attended=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    interview_attend=True
                )
            )
        ).filter(
            interview_attended=True,
            deleted_at__isnull=True  # optional
        ).count() or 0



    
    # rejected_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='rejected').count() or 0
    rejected_students_count= Students.objects.filter(
            deleted_at__isnull=True
        ).annotate(
            has_expired_link_without_attendance=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    expires_at__lt=now(),
                    interview_attend=False
                )
            )
        ).filter(
            has_expired_link_without_attendance=True
        ).count() or 0
    
    pending_interviews_count = Students.objects.filter(
            deleted_at__isnull=True
        ).annotate(
            has_valid_link=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    expires_at__gt=now(),
                    interview_attend=False  # move it here
                )
            )
        ).filter(
            has_valid_link=True
        ).count() or 0
    
    pass_students_count = StudentInterviewLink.objects.filter(
        interview_status='Pass'
    ).count() or 0

    fail_students_count = StudentInterviewLink.objects.filter(
        interview_status='Fail'
    ).count() or 0

    
    # students = Students.objects.filter(
    #     deleted_at__isnull=True, 
    #     edu_doc_verification_status='approved'
    # ).order_by('-id')[:4]

    students = Students.objects.annotate(
        interview_attended=Exists(
            StudentInterviewLink.objects.filter(
                zoho_lead_id=OuterRef('zoho_lead_id'),
                interview_attend=True
            )
        )
    ).filter(
        interview_attended=True,
        edu_doc_verification_status="approved",  # Optional: if only approved students
        deleted_at__isnull=True
    ).order_by('-id')[:4]  # Limit if needed
    
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