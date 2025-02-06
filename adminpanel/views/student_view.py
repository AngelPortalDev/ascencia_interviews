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
        zoho_crm_id =  request.POST.get('ZohoCrmId')
        try:
            data_to_save = {
                'first_name': first_name,
                'last_name': last_name,
                'email':email,
                'dob':formatted_date,
                'phone':phone,
                'student_id':student_id,
                'zoho_crm_id':zoho_crm_id
            }
            result = save_data(Students, data_to_save)
            print(result)
            if result['status']:
                    messages.success(request, "Student updated successfully!")
                    return redirect('institute_list')
            else:
                messages.error(request, result.get('error', "Failed to update the institute."))
                # return render(request, 'institute/institute_update.html', {'institute': institute})

        except Exception as e:
            messages.error(request, f"An error occurred while updating the institute: {e}")
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

            }
            for student in students
        ]
        return render(request, 'student/student.html', {'students': student_data})

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the students: {e}")
        return redirect('admindashboard')  # Redirect to a safe page if needed