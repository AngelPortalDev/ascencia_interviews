
from adminpanel.common_imports import *

def institute_list(request):
    try:
        institutes = Institute.objects.filter(deleted_at__isnull=True)
        institute_data = [
            {
                'crm_id': institute.crm_id,
                'institute_name': institute.institute_name,
                'is_active': institute.is_active,
                'encoded_id': base64_encode(institute.id)
            }
            for institute in institutes
        ]
        print(f"institute_data: {institute_data}")

            
        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('admindashboard')},
            {"name": "Institutes", "url": ""},
        ]

        data = {
            'institutes': institute_data,
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
        }

        return render(request, 'institute/institute.html', data)

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the institutes: {e}")
        return redirect('admindashboard')  # Redirect to a safe page if needed


def institute_add(request):

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Institutes", "url": reverse('institute_list')},
        {"name": "Institute Add", "url": ""},
    ]

    if request.method == 'POST':
        errors = {}
        data = request.POST
        institute_name = data.get('institute_name')
        crm_id = data.get('crm_id')

        if not institute_name:
            errors['institute_name'] = "Institute Name is required."
        else:
            if Institute.objects.filter(institute_name=institute_name, deleted_at__isnull=True).exists():
                errors['institute_name'] = "Institute Name must be unique."

        if not crm_id:
            errors['crm_id'] = "CRM id is required."

        if errors:
            return render(request, 'institute/institute_add.html', {'errors': errors, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items})
        try:
            data_to_save = {
                'institute_name': institute_name,
                'crm_id': crm_id,
            }

            result = save_data(Institute, data_to_save)

            if result['status']:
                messages.success(request, "Institute added successfully!")
                return redirect('institute_list')
            else:
                messages.error(request, "Failed to save the institute. Please try again.")
                return render(request, 'institute/institute_add.html', {"show_breadcrumb": True, "breadcrumb_items": breadcrumb_items,})

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'institute/institute_add.html', {"show_breadcrumb": True, "breadcrumb_items": breadcrumb_items,})

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'institute/institute_add.html', {"show_breadcrumb": True, "breadcrumb_items": breadcrumb_items,})

    data = {
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }

    return render(request, 'institute/institute_add.html', data)


def institute_update(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    institute = get_object_or_404(Institute, id=id)
           
    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Institutes", "url": reverse('institute_list')},
        {"name": "Institute Update", "url": ""},
    ]

    if request.method == 'POST':
        errors = {}
        institute_name = request.POST.get('institute_name')
        crm_id = request.POST.get('crm_id')

        
        if not institute_name:
            errors['institute_name'] = "Institute Name is required."
        else:
            if Institute.objects.filter(institute_name=institute_name).exclude(id=id).exists():
                errors['institute_name'] = "Institute Name must be unique."
        if not crm_id:
            errors['crm_id'] = "CRM id is required."

        if errors:
            return render(request, 'institute/institute_update.html', {'errors': errors, 'institute': institute, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items})

        try:
            data = {
                'institute_name': institute_name,
                'crm_id': crm_id,
            }

            result = save_data(Institute, data, where={'id': id})

            if result['status']:
                messages.success(request, "Institute updated successfully!")
                return redirect('institute_list')
            else:
                messages.error(request, result.get('error', "Failed to update the institute."))
                return render(request, 'institute/institute_update.html', {'institute': institute, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items})

        except Exception as e:
            messages.error(request, f"An error occurred while updating the institute: {e}")
            return render(request, 'institute/institute_update.html', {'institute': institute, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items})

     
    data = {
        'institute': institute,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }

    return render(request, 'institute/institute_update.html', data)


def institute_delete(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    try:
        institute = get_object_or_404(Institute, id=id)

        if institute.deleted_at is not None:
            messages.warning(request, "Institute is already soft deleted.")
        else:
            # Perform the soft delete
            institute.deleted_at = timezone.now()
            institute.soft_delete()
            messages.success(request, "Institute deleted successfully!")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the institute: {e}")

    return redirect('institute_list')


def student_managers_by_institute(request, id):
    id = base64_decode(id)
    institute = get_object_or_404(Institute, id=id)
    encoded_institute_id = base64_encode(institute.id)

    
    studentManagers = User.objects.filter(
        id__in=StudentManagerProfile.objects.filter(institute_id=institute).values_list('user_id', flat=True)
    )

    student_manager_data = [
        {
            'first_name': studentManager.first_name,
            'last_name': studentManager.last_name,
            'email': studentManager.email,
            'encoded_id': base64_encode(studentManager.id),
            'is_active': studentManager.is_active,   # ← THIS WAS MISSING
        }
        for studentManager in studentManagers
    ]

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Institutes", "url": reverse('institute_list')},
        {"name": f"Student Managers - {institute.institute_name}", "url": ""}
    ]

    return render(request, 'student_manager/student_managers_by_institute.html', {
        'student_managers': student_manager_data,
        'institute_name': institute.institute_name,
         'encoded_institute_id': encoded_institute_id,  # <-- IMPORTANT
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    })
    
def toggle_institute_status(request, id):
    id = base64_decode(id)
    institute = get_object_or_404(Institute, id=id)
    institute.is_active = not institute.is_active
    institute.save()
    status = "activated" if institute.is_active else "deactivated"
    messages.success(request, f"Institution has been {status}.")
    return redirect('institute_list')



def toggle_student_manager_status_in_institute(request, id, institute_id):
    id = base64_decode(id)
    institute_id = base64_decode(institute_id)

    user = get_object_or_404(User, id=id)
    user.is_active = not user.is_active
    user.save()

    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"Student Manager has been {status}.")

    # Redirect back to the SAME institute manager list
    encoded_institute_id = base64_encode(institute_id)
    return redirect('student_managers_by_institute', id=encoded_institute_id)
