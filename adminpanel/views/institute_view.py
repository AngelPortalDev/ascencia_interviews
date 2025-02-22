
from adminpanel.common_imports import *

def institute_list(request):
    try:
        institutes = Institute.objects.filter(deleted_at__isnull=True)
        institute_data = [
            {
                'institute_id': institute.institute_id,
                'institute_name': institute.institute_name,
                'encoded_id': base64_encode(institute.id)
            }
            for institute in institutes
        ]
            
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
    if request.method == 'POST':
        errors = {}
        data = request.POST
        institute_name = data.get('institute_name')
        institute_id = data.get('institute_id')

        if not institute_name:
            errors['institute_name'] = "Institute Name is required."
        if not institute_id:
            errors['institute_id'] = "Institute id is required."

        if errors:
            return render(request, 'institute/institute_add.html', {'errors': errors})
        try:
            data_to_save = {
                'institute_name': institute_name,
                'institute_id': institute_id,
            }

            result = save_data(Institute, data_to_save)

            if result['status']:
                messages.success(request, "Institute added successfully!")
                return redirect('institute_list')
            else:
                messages.error(request, "Failed to save the institute. Please try again.")
                return render(request, 'institute/institute_add.html')

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'institute/institute_add.html')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'institute/institute_add.html')

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Institutes", "url": reverse('institute_list')},
        {"name": "Institute Add", "url": ""},
    ]
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

    if request.method == 'POST':
        errors = {}
        institute_name = request.POST.get('institute_name')
        institute_id = request.POST.get('institute_id')

        
        if not institute_name:
            errors['institute_name'] = "Institute Name is required."
        if not institute_id:
            errors['institute_id'] = "Institute id is required."

        if errors:
            return render(request, 'institute/institute_update.html', {'errors': errors})

        try:
            data = {
                'institute_name': institute_name,
                'institute_id': institute_id,
            }

            result = save_data(Institute, data, where={'id': id})

            if result['status']:
                messages.success(request, "Institute updated successfully!")
                return redirect('institute_list')
            else:
                messages.error(request, result.get('error', "Failed to update the institute."))
                return render(request, 'institute/institute_update.html', {'institute': institute})

        except Exception as e:
            messages.error(request, f"An error occurred while updating the institute: {e}")
            return render(request, 'institute/institute_update.html', {'institute': institute})

            
    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Institutes", "url": reverse('institute_list')},
        {"name": "Institute Update", "url": ""},
    ]
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
