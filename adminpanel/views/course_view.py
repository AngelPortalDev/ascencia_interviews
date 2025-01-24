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
        courses = Course.active_objects.all()
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
        return redirect('admindashboard') 

@login_required
def course_add(request):

    institutes = Institute.objects.filter(deleted_at__isnull=True)
    errors = {}
    if request.method == 'POST':
        data = request.POST
        course_name = data.get('course_name')
        institute_id = data.get('institute_id')

        if not course_name:
            errors['course_name'] = "Course Name is required."
        if not institute_id:
            errors['institute_id'] = "Institute is required."

        if errors:
            return render(request, 'course/course_add.html', {'institutes': institutes, 'errors': errors})
        try:
            institute = Institute.objects.get(id=institute_id)
            data_to_save = {
                'course_name': course_name,
                'institute_id': institute,
            }

            result = save_data(Course, data_to_save)

            if result['status']:
                messages.success(request, "Course added successfully!")
                return redirect('courses')
            else:
                messages.error(request, "Failed to save the course. Please try again.")
                return render(request, 'course/course_add.html', {'institutes': institutes})

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'course/course_add.html', {'institutes': institutes})

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'course/course_add.html', {'institutes': institutes})


    
    return render(request, 'course/course_add.html', {'institutes': institutes})


@login_required
def course_update(request, id):
    id = base64_decode(id)

    institutes = Institute.objects.filter(deleted_at__isnull=True)
    errors = {}

    if not id:
        return HttpResponse("Invalid ID", status=400)

    course = get_object_or_404(Course, id=id)

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        institute_id = request.POST.get('institute_id')

        if not course_name:
            errors['course_name'] = "Course Name is required."
        if not institute_id:
            errors['institute_id'] = "Institute is required."

        if errors:
            return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes, 'errors': errors})

        try:
            institute = Institute.objects.get(id=institute_id)
            data = {
                'course_name': course_name,
                'institute_id': institute,
            }

            result = save_data(Course, data, where={'id': id})

            if result['status']:
                messages.success(request, "Institute updated successfully!")
                return redirect('courses')
            else:
                messages.error(request, result.get('error', "Failed to update the course."))
                return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes })

        except Exception as e:
            messages.error(request, f"An error occurred while updating the institute: {e}")
            return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes })

    return render(request, 'course/course_update.html', {'course': course, 'institutes': institutes })


@login_required
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
