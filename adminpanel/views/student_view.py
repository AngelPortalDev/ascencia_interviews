import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from datetime import datetime



@csrf_exempt  # Disable CSRF for webhooks
def students_leads_api(request):
    if request.method == "POST":
        first_name = request.POST.get('First Name')
        last_name = request.POST.get('Last Name')
        email = request.POST.get('Email')
        phone = request.POST.get('Phone')
        dob = request.POST.get('DOB')
        date_object = datetime.strptime(dob, "%d-%m-%Y")
        formatted_date = date_object.strftime("%Y-%m-%d")
        student_id = request.POST.get('UserId')
        zoho_lead_id =  request.POST.get('Zoho Lead Id')
        program =  request.POST.get('Program')
        intake_year =  request.POST.get('Intake Year')
        intake_month =  request.POST.get('Intake Month')
        student_manager_email = request.POST.get('Student Manager Email')
        crm_id = request.POST.get('CRM Id')
        
        

        try:
            data_to_save = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'dob': formatted_date,
                'phone': phone,
                'student_id': student_id,
                'zoho_lead_id': zoho_lead_id, 
                'program': program,
                'intake_year': intake_year,
                'intake_month': intake_month,
                'student_manager_email': student_manager_email,
                'crm_id': crm_id,
            }

            where = {"zoho_lead_id": zoho_lead_id}

            result = save_data(Students, data_to_save, where)
            # print(r'result:', result)

            if result['status']:
                return JsonResponse({"status": True, "message": "Student updated successfully!"}, status=200)
            else:
                return JsonResponse({"status": False, "error": result.get('error', "Failed to update the student.")}, status=400)

        except Exception as e:
            return JsonResponse({"status": False, "error": str(e)}, status=500)

    return JsonResponse({"status": False, "error": "Invalid request method"}, status=405)


# def students_list(request):
#     try:
#         students = Students.objects.filter(deleted_at__isnull=True)
#         student_data = [
#             {
#                 'id': student.student_id,
#                 'first_name': student.first_name,
#                 'last_name': student.last_name,
#                 'email': student.email,
#                 'phone': student.phone,
#                 'program': student.program,
#                 'zoho_lead_id': student.zoho_lead_id,

#             }
#             for student in students
#         ]
#         return render(request, 'student/student.html', {'students': student_data})

#     except Exception as e:
#         messages.error(request, f"An error occurred while fetching the students: {e}")
#         return redirect('admindashboard')

def students_list(request):
    try:
        students = Students.objects.order_by('-id').filter(deleted_at__isnull=True)
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
                    'edu_doc_verification_status': getattr(student, 'edu_doc_verification_status', '') or '',
                    'intake_year': getattr(student, 'intake_year', '') or '',
                    'intake_month': getattr(student, 'intake_month', '') or '',
                    'zoho_lead_id': getattr(student, 'zoho_lead_id', '') or '',
                }
                for student in queryset
            ]
            
        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('admindashboard')},
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
        return redirect('admindashboard')




def student_detail(request, zoho_lead_id):
    student = get_object_or_404(Students, zoho_lead_id=zoho_lead_id)
    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Students", "url": reverse('students_list')},
        {"name": f"{student.first_name} {student.last_name}", "url": ""}
    ]

    return render(request, "student/student_detail.html", {
        "student": student,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items
    })