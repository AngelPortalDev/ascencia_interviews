
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from studentpanel.models.interview_link import StudentInterviewLink
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Exists

from django.utils.timezone import now
from django.db.models import Q
from django.utils import timezone
def student_manager_dashboard(request):
    user_email = request.user.email
    students_count = Students.objects.filter(deleted_at__isnull=True, student_manager_email=request.user.email ).count()
    
    # verified_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='approved', student_manager_email=request.user.email ).count() or 0
    verified_students_count = Students.objects.annotate(
    interview_attended=Exists(
        StudentInterviewLink.objects.filter(
            zoho_lead_id=OuterRef('zoho_lead_id'),
            interview_attend=True
        )
    )
    ).filter(
        interview_attended=True,
        deleted_at__isnull=True,
        edu_doc_verification_status='approved',
        student_manager_email=request.user.email
    ).count() or 0
    


    # rejected_students_count = Students.objects.filter(deleted_at__isnull=True, edu_doc_verification_status='rejected', student_manager_email=request.user.email ).count() or 0

    rejected_students_count = (
    Students.objects.filter(deleted_at__isnull=True)
    .annotate(
        has_expired_link_without_attendance=Exists(
            StudentInterviewLink.objects.filter(
                zoho_lead_id=OuterRef('zoho_lead_id'),
                expires_at__lt=now(),
                interview_attend=False
            )
        )
    )
    .filter(
        has_expired_link_without_attendance=True,
        student_manager_email=request.user.email
    )
    .count() or 0
)
    
    valid_students = Students.objects.filter(
        deleted_at__isnull=True,
        student_manager_email=request.user.email,
        zoho_lead_id=OuterRef('zoho_lead_id')
    )

    # Pending Interviews Count
    # pending_interviews_count = StudentInterviewLink.objects.filter(
    #     expires_at__gt=timezone.now(),
    #     is_expired=0,
    #     zoho_lead_id__in=Subquery(valid_students.values("zoho_lead_id"))
    # ).count() or 0

    pending_interviews_count = (
    Students.objects.filter(
        deleted_at__isnull=True,
        student_manager_email=request.user.email  # ✅ Add this filter
    )
    .annotate(
        has_valid_link=Exists(
            StudentInterviewLink.objects.filter(
                zoho_lead_id=OuterRef('zoho_lead_id'),
                expires_at__gt=timezone.now(),
                interview_attend=False
            ).filter(
                Q(is_expired=False) | Q(is_expired__isnull=True)
            )
        )
    )
    .filter(has_valid_link=True)
    .count() or 0
)

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
    
    # students_with_interview_status = []
    # for student in students:
    #     interview_status = StudentInterviewLink.objects.filter(zoho_lead_id=student.zoho_lead_id).first()
    #     students_with_interview_status.append({
    #         'student': student,
    #         'interview_status': interview_status.interview_status if interview_status else 'Not Available'
    #     })


     # Latest 4 Students who have attended at least one interview
    students_attended = Students.objects.filter(deleted_at__isnull=True, student_manager_email=user_email)\
        .annotate(
            interview_attended=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    interview_attend=True
                )
            )
        ).filter(interview_attended=True).order_by('-id')[:4]

    students_with_interview_status = []
    for student in students_attended:
        latest_interview = StudentInterviewLink.objects.filter(
            zoho_lead_id=student.zoho_lead_id,
            interview_attend=True
        ).order_by('-id').first()
        students_with_interview_status.append({
            'student': student,
            'interview_status': latest_interview.interview_status if latest_interview else 'Not Available'
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
