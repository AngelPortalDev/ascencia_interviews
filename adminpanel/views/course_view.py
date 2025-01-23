from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from adminpanel.models.course import Course
from adminpanel.models.institute import Institute
from adminpanel.helpers import save_data, base64_encode, base64_decode
from django.core.exceptions import ValidationError
from django.utils import timezone


@login_required
def courses(request):
    try:
        courses = Course.objects.filter(deleted_at__isnull=True)
        course_data = [
            {
                'course_name': course.course_name,
                'institute_id': course.institute_id,
                'encoded_id': base64_encode(course.id)
            }
            for course in courses
        ]

        return render(request, 'course/course.html', {'courses': course_data})

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the courses: {e}")
        return redirect('index') 

@login_required
def course_add(request):
    if request.method == 'POST':
        data = request.POST
        course_name = data.get('course_name')
        institute_id = data.get('institute_id')

        if not course_name or not institute_id:
            messages.error(request, "Both Course Name and Institute ID are required.")
            return render(request, 'course/course_add.html')

        try:
            data_to_save = {
                'course_name': course_name,
                'institute_id': institute_id,
            }

            result = save_data(Course, data_to_save)

            if result['status']:
                messages.success(request, "Course added successfully!")
                return redirect('courses')
            else:
                messages.error(request, "Failed to save the course. Please try again.")
                return render(request, 'course/course_add.html')

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'course/course_add.html')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'course/course_add.html')


    institutes = Institute.objects.filter(deleted_at__isnull=True)
    institute_data = [
        {
            'institute_name': institute.institute_name,
            'institute_id': institute.id
        }
        for institute in institutes
    ]
    
    return render(request, 'course/course_add.html', {'institutes': institute_data})


# @login_required
# def institute_update(request, id):
#     id = base64_decode(id)

#     if not id:
#         return HttpResponse("Invalid or tampered ID", status=400)

#     institute = get_object_or_404(Institute, id=id)

#     if request.method == 'POST':
#         institute_name = request.POST.get('institute_name')
#         institute_id = request.POST.get('institute_id')

#         if not institute_name or not institute_id:
#             messages.error(request, "Both Institute Name and Institute ID are required.")
#             return render(request, 'institute/institute_update.html', {'institute': institute})

#         try:
#             data = {
#                 'institute_name': institute_name,
#                 'institute_id': institute_id,
#             }

#             result = save_data(Institute, data, where={'id': id})

#             if result['status']:
#                 messages.success(request, "Institute updated successfully!")
#                 return redirect('courses')
#             else:
#                 messages.error(request, result.get('error', "Failed to update the institute."))
#                 return render(request, 'institute/institute_update.html', {'institute': institute})

#         except Exception as e:
#             messages.error(request, f"An error occurred while updating the institute: {e}")
#             return render(request, 'institute/institute_update.html', {'institute': institute})

#     return render(request, 'institute/institute_update.html', {'institute': institute})


# @login_required
# def institute_delete(request, id):
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
            institute.save()
            messages.success(request, "Institute deleted successfully!")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the institute: {e}")

    return redirect('courses')
