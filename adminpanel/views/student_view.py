import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from datetime import datetime



@csrf_exempt  # Disable CSRF for webhooks
def students_leads_api(request):
    if request.method == "POST":
        # Get form data using request.POST
        first_name = request.POST.get('First Name')
        last_name = request.POST.get('Last Name')
        email = request.POST.get('Email')
        phone = request.POST.get('Phone')
        dob = request.POST.get('DOB')
        date_object = datetime.strptime(dob, "%d-%m-%Y")
        formatted_date = date_object.strftime("%Y-%m-%d")
        student_id = request.POST.get('UserId')
        zoho_lead_id =  request.POST.get('ZohoCrmId')
        program =  request.POST.get('Program')
        
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
            # return render(request, 'institute/institute_update.html', {'institute': institute})
    
# def students_list(request):

#     students_list = Students.objects.all()
#     print("Rendering students list:", students_list)  # Debugging line
#     return render(request, 'student/student.html', {'students': students_list})


def students_list(request):
    try:
        students = Students.objects.filter(deleted_at__isnull=True)
        student_data = [
            {
                'id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone,
                'zoho_lead_id': student.zoho_lead_id,

            }
            for student in students
        ]
        return render(request, 'student/student.html', {'students': student_data})

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the students: {e}")
        return redirect('admindashboard')  # Redirect to a safe page if needed



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