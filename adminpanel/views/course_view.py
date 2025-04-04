
from adminpanel.common_imports import *

def courses(request):
    try:
        # courses = Course.active_objects.all().order_by('-id')
        courses = Course.active_objects.all().order_by('-created_at')
        course_data = [
            {
                'course_name': course.course_name,
                'crm_id': course.crm_id,
                'encoded_id': base64_encode(course.id)
            }
            for course in courses
        ]
          
        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('admindashboard')},
            {"name": "Courses", "url": ""},
        ]
        data = {
            'courses': course_data,
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
        }

        # print(r'result', course_data)
        return render(request, 'course/course.html', data)

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the courses: {e}")
        return redirect('admindashboard') 

# def course_add(request):

#     institutes = Institute.objects.filter(deleted_at__isnull=True)
#     errors = {}
#     if request.method == 'POST':
#         data = request.POST
#         course_name = data.get('course_name')
#         crm_id = data.get('crm_id')

#         if not course_name:
#             errors['course_name'] = "Course Name is required."
#         if not crm_id:
#             errors['crm_id'] = "Institute is required."

#         if errors:
#             return render(request, 'course/course_add.html', {'institutes': institutes, 'errors': errors})
#         try:
#             institute = Institute.objects.get(id=crm_id)
#             data_to_save = {
#                 'course_name': course_name,
#                 'crm_id': institute,
#             }

#             result = save_data(Course, data_to_save)

#             if result['status']:
#                 messages.success(request, "Course added successfully!")
#                 return redirect('courses')
#             else:
#                 messages.error(request, "Failed to save the course. Please try again.")
#                 return render(request, 'course/course_add.html', {'institutes': institutes})

#         except IntegrityError as e:
#             messages.error(request, "A database error occurred. Please try again later.")
#             return render(request, 'course/course_add.html', {'institutes': institutes})

#         except Exception as e:
#             messages.error(request, f"An error occurred: {e}")
#             return render(request, 'course/course_add.html', {'institutes': institutes})


#     breadcrumb_items = [
#         {"name": "Dashboard", "url": reverse('admindashboard')},
#         {"name": "Courses", "url": reverse('courses')},
#         {"name": "Course Add", "url": ""},
#     ]
#     data = {
#         'institutes': institutes,
#         "show_breadcrumb": True,
#         "breadcrumb_items": breadcrumb_items,
#     }
    
#     return render(request, 'course/course_add.html', data)


def course_add(request):
    institutes = Institute.objects.filter(deleted_at__isnull=True)
    errors = {}

    if request.method == 'POST':
        data = request.POST
        course_name = data.get('course_name')
        crm_id = data.get('crm_id')

        if not course_name:
            errors['course_name'] = "Course Name is required."
        if not crm_id:
            errors['crm_id'] = "Institute is required."

        if errors:
            return render(request, 'course/course_add.html', {'institutes': institutes, 'errors': errors})

        try:
            institute = Institute.objects.get(id=crm_id)

            # Check if the course already exists for the same institute
            if Course.objects.filter(course_name=course_name, crm_id=institute).exists():
                messages.error(request, "This course is already assigned to the selected institute.")
                return render(request, 'course/course_add.html', {'institutes': institutes})

            # Save the new course
            data_to_save = {
                'course_name': course_name,
                'crm_id': institute,
            }

            result = save_data(Course, data_to_save)

            if result['status']:
                messages.success(request, "Course added successfully!")
                return redirect('courses')
            else:
                messages.error(request, "Failed to save the course. Please try again.")

        except IntegrityError:
            messages.error(request, "A database error occurred. Please try again later.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, 'course/course_add.html', {'institutes': institutes})


# def course_update(request, id):
#     id = base64_decode(id)

#     institutes = Institute.objects.filter(deleted_at__isnull=True)
#     errors = {}

#     if not id:
#         return HttpResponse("Invalid ID", status=400)

#     course = get_object_or_404(Course, id=id)

#     if request.method == 'POST':
#         course_name = request.POST.get('course_name')
#         crm_id = request.POST.get('crm_id')

#         if not course_name:
#             errors['course_name'] = "Course Name is required."
#         if not crm_id:
#             errors['crm_id'] = "Institute is required."

#         if errors:
#             return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes, 'errors': errors})

#         try:
#             institute = Institute.objects.get(id=crm_id)
#             data = {
#                 'course_name': course_name,
#                 'crm_id': institute,
#             }

#             result = save_data(Course, data, where={'id': id})

#             if result['status']:
#                 messages.success(request, "Course updated successfully!")
#                 return redirect('courses')
#             else:
#                 messages.error(request, result.get('error', "Failed to update the course."))
#                 return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes })

#         except Exception as e:
#             messages.error(request, f"An error occurred while updating the course: {e}")
#             return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes })

#     breadcrumb_items = [
#         {"name": "Dashboard", "url": reverse('admindashboard')},
#         {"name": "Courses", "url": reverse('courses')},
#         {"name": "Course Update", "url": ""},
#     ]
#     data = {
#         'course': course, 
#         'institutes': institutes,
#         "show_breadcrumb": True,
#         "breadcrumb_items": breadcrumb_items,
#     }

#     return render(request, 'course/course_update.html', data)


def course_update(request, id):
    id = base64_decode(id)

    institutes = Institute.objects.filter(deleted_at__isnull=True)
    errors = {}

    if not id:
        return HttpResponse("Invalid ID", status=400)

    course = get_object_or_404(Course, id=id)

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        crm_id = request.POST.get('crm_id')

        if not course_name:
            errors['course_name'] = "Course Name is required."
        if not crm_id:
            errors['crm_id'] = "Institute is required."

        if errors:
            return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes, 'errors': errors})

        try:
            institute = Institute.objects.get(id=crm_id)

            # Check if the updated course name is already assigned to this institute (excluding the current course)
            if Course.objects.filter(course_name=course_name, crm_id=institute).exclude(id=id).exists():
                messages.error(request, "This course is already assigned to the selected institute.")
                return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes})

            # Update course data
            course.course_name = course_name
            course.crm_id = institute
            course.save()

            messages.success(request, "Course updated successfully!")
            return redirect('courses')

        except IntegrityError:
            messages.error(request, "A database error occurred. Please try again later.")
        except Exception as e:
            messages.error(request, f"An error occurred while updating the course: {e}")

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Courses", "url": reverse('courses')},
        {"name": "Course Update", "url": ""},
    ]
    data = {
        'course': course, 
        'institutes': institutes,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }

    return render(request, 'course/course_update.html', data)



def course_delete(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    try:
        course = get_object_or_404(Course, id=id)

        if course.deleted_at is not None:
            messages.warning(request, "Course is already soft deleted.")
        else:
            # Perform the soft delete
            course.deleted_at = timezone.now()
            course.soft_delete()
            messages.success(request, "Course deleted successfully!")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the course: {e}")

    return redirect('courses')
