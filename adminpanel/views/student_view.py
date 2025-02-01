import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from datetime import datetime
@csrf_exempt  # Disable CSRF for webhooks
def students(request):
    if request.method == "POST":
        # Get form data using request.POST
        # print(request.POST.get)
        first_name = request.POST.get('First Name')
        last_name = request.POST.get('Last Name')
        email = request.POST.get('Email')
        phone = request.POST.get('Phone')
        dob = request.POST.get('DOB')
        date_object = datetime.strptime(dob, "%d-%m-%Y")
        formatted_date = date_object.strftime("%Y-%m-%d")
       
        try:
            data_to_save = {
                'first_name': first_name,
                'last_name': last_name,
                'email':email,
                'dob':formatted_date,
                'phone':phone,
                'student_id':"12",
                'student_consent':"12",
                'answers_scores': '100',
                'sentiment_score':'30'
            }
            # print(data_to_save)
            result = save_data(Students, data_to_save)
            # print(result)

            if result['status']:
                    messages.success(request, "Student updated successfully!")
                    return redirect('institute_list')
            else:
                messages.error(request, result.get('error', "Failed to update the institute."))
                # return render(request, 'institute/institute_update.html', {'institute': institute})

        except Exception as e:
            messages.error(request, f"An error occurred while updating the institute: {e}")
            # return render(request, 'institute/institute_update.html', {'institute': institute})