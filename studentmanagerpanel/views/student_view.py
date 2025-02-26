import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from datetime import datetime


def students_list(request):
    try:
        students = Students.objects.filter(deleted_at__isnull=True,student_manager_email=request.user.email ).order_by('-id')
        verified_students = students.filter(edu_doc_verification_status="approved")
        rejected_students = students.filter(edu_doc_verification_status="rejected")

        def format_student_data(queryset):
            return [
                {
                    'id': student.student_id,
                    'first_name': getattr(student, 'first_name', '') or '',
                    'last_name': getattr(student, 'last_name', '') or '',
                    'email': getattr(student, 'email', '') or '',
                    'phone': getattr(student, 'phone', '') or '',
                    'program': getattr(student, 'program', '') or '',
                    'intake_year': getattr(student, 'intake_year', '') or '',
                    'intake_month': getattr(student, 'intake_month', '') or '',
                    'zoho_lead_id': getattr(student, 'zoho_lead_id', '') or '',
                }
                for student in queryset
            ]
            
        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('studentmanagerdashboard')},
            {"name": "Students", "url": ""},
        ]

        context = {
            'all_students': format_student_data(students),
            'verified_students': format_student_data(verified_students),
            'rejected_students': format_student_data(rejected_students),
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
        }

        return render(request, 'student/student.html', context)
        
    except Exception as e:
        messages.error(request, f"An error occurred while fetching the students: {e}")
        return redirect('studentmanagerdashboard')

        


def student_detail(request, zoho_lead_id):
    student = get_object_or_404(Students, zoho_lead_id=zoho_lead_id)
    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('studentmanagerdashboard')},
        {"name": "Students", "url": reverse('studentmanager_students_list')},
        {"name": f"{student.first_name} {student.last_name}", "url": ""}
    ]


    return render(request, "student/student_detail.html", {
        "student": student,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items
    })