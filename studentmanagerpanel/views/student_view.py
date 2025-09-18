import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from datetime import datetime
from studentpanel.models.interview_link import StudentInterviewLink
import calendar
from django.conf import settings
from django.db.models import OuterRef, Subquery, Exists
from django.utils.timezone import now
def students_list(request):
    try:
        # students = Students.objects.filter(deleted_at__isnull=True,student_manager_email=request.user.email ).order_by('-id')
         # 1️⃣ Base queryset depending on role
        if hasattr(request.user, 'profile') and request.user.profile.role == 1:
            # Student Manager — only their assigned students
            students = Students.objects.filter(
                deleted_at__isnull=True,
                student_manager_email=request.user.email
            )
        else:
            # Admin — all students
            students = Students.objects.filter(deleted_at__isnull=True)

         # 2️⃣ Intake Month & Year filters
        intake_month = request.GET.get('intake_month', '')
        intake_year = request.GET.get('intake_year', '')

        filter_kwargs = {}
        if intake_month:
            filter_kwargs['intake_month'] = intake_month
        if intake_year.isdigit():
            filter_kwargs['intake_year'] = int(intake_year)

        students = students.filter(**filter_kwargs)

        # verified_students = students.filter(edu_doc_verification_status="approved")
        # rejected_students = students.filter(edu_doc_verification_status="rejected")
        # unverified_students = students.filter(edu_doc_verification_status="Unverified")

        # 3️⃣ Verified Students — attended at least one interview
        latest_link_subquery = StudentInterviewLink.objects.filter(
            zoho_lead_id=OuterRef('zoho_lead_id'),
            interview_attend=True
        ).order_by('-id').values('id')[:1]

        verified_students = students.annotate(
            latest_interview_id=Subquery(latest_link_subquery)
        ).filter(latest_interview_id__isnull=False).order_by('-latest_interview_id')

        # 4️⃣ Rejected Students — unexpired, unattended interview link
        rejected_students = students.annotate(
            has_valid_link=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    expires_at__gt=now(),
                    interview_attend=False
                )
            )
        ).filter(has_valid_link=True).order_by('-id')

        # 5️⃣ Unverified Students — expired and not attended interview link
        unverified_students = students.annotate(
            has_expired_link_without_attendance=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    expires_at__lt=now(),
                    interview_attend=False
                )
            )
        ).filter(has_expired_link_without_attendance=True).order_by('-id')

        active_tab = request.GET.get('tab', 'all')  # default tab is 'all'

        def get_interview_status(student):
            link = StudentInterviewLink.objects.filter(
                zoho_lead_id=student.zoho_lead_id
            ).order_by('-id').first()

            if not link:
                return "Not Sent"

            if link.interview_attend:
                if student.bunny_stream_video_id:
                    return 'Interview Done <span style="display:inline-block;width:8px;height:8px;background-color:green;border-radius:50%;margin-left:4px;"></span>'
                else:
                    return 'Interview Done <span style="display:inline-block;width:8px;height:8px;background-color:red;border-radius:50%;margin-left:4px;"></span>'

            if link.expires_at and link.expires_at < timezone.now():
                return "Expired"

            if link.interview_link_count == "MQ==":
                return "First Link Active"
            if link.interview_link_count == "Mg==":
                return "Second Link Active"

            return "Pending"

        def format_student_data(queryset):
            return [
                {
                    'id': student.student_id,
                    'first_name': getattr(student, 'first_name', '') or '',
                    'last_name': getattr(student, 'last_name', '') or '',
                    'email': getattr(student, 'email', '') or '',
                    'phone': getattr(student, 'phone', '') or '',
                    'program': getattr(student, 'program', '') or '',
                    'edu_doc_verification_status': getattr(student, 'edu_doc_verification_status', '') or '',
                    'intake_year': getattr(student, 'intake_year', '') or '',
                    'intake_month': getattr(student, 'intake_month', '') or '',
                    'zoho_lead_id': getattr(student, 'zoho_lead_id', '') or '',
                    'interview_status': get_interview_status(student),  # ✅ Added here
                }
                for student in queryset
            ]
        months = list(calendar.month_name)[1:]  # ['January', 'February', ...]
        years = list(range(2022, 2041))

        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('studentmanagerdashboard')},
            {"name": "Students", "url": ""},
        ]

        context = {
            'all_students': format_student_data(students),
            'verified_students': format_student_data(verified_students),
            'rejected_students': format_student_data(rejected_students),
            'unverified_students': format_student_data(unverified_students),
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
            "intake_months": months,
            "intake_years": years,
            "selected_intake_month": intake_month,
            "selected_intake_year": intake_year,
            'active_tab': active_tab,  # 🔹 Send active tab to template
        }

        return render(request, 'student/student.html', context)
        
    except Exception as e:
        messages.error(request, f"An error occurred while fetching the students: {e}")
        return redirect('studentmanagerdashboard')

        


def student_detail(request, zoho_lead_id):


    student = get_object_or_404(Students, zoho_lead_id=zoho_lead_id)


     
    # Get the latest interview link (even if transcript is empty)
    interview_link = (
        StudentInterviewLink.objects
        .filter(zoho_lead_id=zoho_lead_id)
        .order_by("-id")
        .first()
    )

    transcript_text = (
        interview_link.transcript_text 
        if interview_link and interview_link.transcript_text 
        else "Transcript not available."
    )

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('studentmanagerdashboard')},
        {"name": "Students", "url": reverse('studentmanager_students_list')},
        {"name": f"{student.first_name} {student.last_name}", "url": ""}
    ]


    return render(request, "student/student_detail.html", {
        "student": student,
        "show_breadcrumb": True,
        "transcript_text": transcript_text,
        "breadcrumb_items": breadcrumb_items,
        "BUNNY_STREAM_LIBRARY_ID": getattr(settings, 'BUNNY_STREAM_LIBRARY_ID', None)  # For video access

    })