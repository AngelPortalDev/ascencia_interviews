
from adminpanel.common_imports import *

def student_managers(request):
    try:
        studentManagers = StudentManager.active_objects.all()
        student_manager_data = [
            {
                'first_name': studentManager.first_name,
                'last_name': studentManager.last_name,
                'email': studentManager.email,
                'institute_id': studentManager.institute_id,
                'encoded_id': base64_encode(studentManager.id)
            }
            for studentManager in studentManagers
        ]

        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('admindashboard')},
            {"name": "Student Managers", "url": ""},
        ]
        data = {
            'student_managers': student_manager_data,
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
        }

        print(r'result', student_manager_data)
        return render(request, 'student_manager/student_manager.html', data)

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the questions: {e}")
        return redirect('admindashboard') 


def student_manager_add(request):
    institutes = Institute.objects.filter(deleted_at__isnull=True)
    if request.method == 'POST':
        errors = {}
        data = request.POST
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        institute_id = data.get('institute_id')

        if not first_name:
            errors['first_name'] = "First Name is required."
        if not last_name:
            errors['last_name'] = "Last Name is required."
        if not email:
            errors['email'] = "Email is required."
        if not institute_id:
            errors['institute_id'] = "Institute is required."

        if errors:
            return render(request, 'student_manager/student_manager_add.html', {'institutes': institutes, 'errors': errors, })
        try:
            institute = Institute.objects.get(id=institute_id)
            data_to_save = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'institute_id': institute,
            }

            result = save_data(StudentManager, data_to_save)

            if result['status']:
                messages.success(request, "Student Manager added successfully!")
                return redirect('student_managers')
            else:
                messages.error(request, "Failed to save the student manager. Please try again.")
                return render(request, 'student_manager/student_manager_add.html', {'institutes': institutes})

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'student_manager/student_manager_add.html', {'institutes': institutes})

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'student_manager/student_manager_add.html', {'institutes': institutes})

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Student Managers", "url": reverse('student_managers')},
        {"name": "Student Manager Add", "url": ""},
    ]
    data = {
        'institutes': institutes,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }

    return render(request, 'student_manager/student_manager_add.html', data)


def student_manager_update(request, id):
    id = base64_decode(id)

    institutes = Institute.objects.filter(deleted_at__isnull=True)
    errors = {}

    if not id:
        return HttpResponse("Invalid ID", status=400)

    student_manager = get_object_or_404(StudentManager, id=id)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        institute_id = request.POST.get('institute_id')

        if not first_name:
            errors['first_name'] = "First Name is required."
        if not last_name:
            errors['last_name'] = "First Name is required."
        if not email:
            errors['email'] = "First Name is required."
        if not institute_id:
            errors['institute_id'] = "Institute is required."

        if errors:
            return render(request, 'student_manager/student_manager_update.html', {'student_manager': student_manager, 'institutes': institutes, 'errors': errors})

        try:
            institute = Institute.objects.get(id=institute_id)
            data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'institute_id': institute,
            }

            result = save_data(StudentManager, data, where={'id': id})

            if result['status']:
                messages.success(request, "Student Manager updated successfully!")
                return redirect('student_managers')
            else:
                messages.error(request, result.get('error', "Failed to update the student manager."))
                return render(request, 'student_manager/student_manager_update.html', {'student_manager': student_manager, 'institutes': institutes })

        except Exception as e:
            messages.error(request, f"An error occurred while updating the student manager: {e}")
            return render(request, 'student_manager/student_manager_update.html', {'student_manager': student_manager, 'institutes': institutes })

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Student Managers", "url": reverse('student_managers')},
        {"name": "Student Manager Update", "url": ""},
    ]
    data = {
        'student_manager': student_manager, 
        'institutes': institutes,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }

    return render(request, 'student_manager/student_manager_update.html', data)



def student_manager_delete(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    try:
        student_manager = get_object_or_404(StudentManager, id=id)

        if student_manager.deleted_at is not None:
            messages.warning(request, "Record is already soft deleted.")
        else:
            # Perform the soft delete
            student_manager.deleted_at = timezone.now()
            student_manager.soft_delete()
            messages.success(request, "Record deleted successfully!")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the student manager: {e}")

    return redirect('student_managers')
