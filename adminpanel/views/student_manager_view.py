
from adminpanel.common_imports import *
from django.contrib.auth import get_user_model
from adminpanel.models.user_role import UserRoles
from django.http import HttpResponse
from studentpanel.models.interview_process_model import Students
from django.contrib.auth.hashers import make_password
import re

User = get_user_model()

def student_managers(request):
    try:
        # studentManagers = StudentManagerProfile.active_objects.all()
        studentManagers = User.objects.filter(
            id__in=UserRoles.objects.filter(role=1).values_list('user_id', flat=True)
        )

        student_manager_data = [
            {
                'first_name': studentManager.first_name,
                'last_name': studentManager.last_name,
                'email': studentManager.email,
                # 'institute_id': studentManager.institute_id,
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
        password = data.get("password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()

        # Validation
        if not first_name:
            errors['first_name'] = "First Name is required."
        if not last_name:
            errors['last_name'] = "Last Name is required."
        if not email:
            errors['email'] = "Email is required."
        if not institute_id:
            errors['institute_id'] = "Institute is required."
        if not password:
            errors['password'] = "Password is required."
        if not confirm_password:
            errors['confirm_password'] = "Confirm Password is required."
             
        if password:
            if len(password) < 8:
                errors['password'] = "Password must be at least 8 characters long."
            if not re.search(r'[A-Z]', password):
                errors['password'] = "Password must contain at least one uppercase letter."
            if not re.search(r'[a-z]', password):
                errors['password'] = "Password must contain at least one lowercase letter."
            if not re.search(r'\d', password):
                errors['password'] = "Password must contain at least one digit."
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors['password'] = "Password must contain at least one special character."
            if password != confirm_password:
                errors['confirm_password'] = "Passwords do not match."

        if errors:
            return render(request, 'student_manager/student_manager_add.html', {'institutes': institutes, 'errors': errors})

        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=email
                )
                if password:
                    user.password = make_password(password)
                user.save()

                # Assign Role
                UserRoles.objects.create(user=user, role=1)  # Assuming 1 = Student Manager

                # Store user_id & institute_id in StudentManagerProfile
                institute = Institute.objects.get(id=institute_id)
                StudentManagerProfile.objects.create(user=user, institute_id=institute)

            messages.success(request, "Student Manager added successfully!")
            return redirect('student_managers')

        except IntegrityError:
            messages.error(request, "A database error occurred. Please try again later.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Student Managers", "url": reverse('student_managers')},
        {"name": "Student Manager Add", "url": ""},
    ]
    
    return render(request, 'student_manager/student_manager_add.html', {
        'institutes': institutes,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    })


def student_manager_update(request, id):
    id = base64_decode(id) 
    errors = {}

    if not id:
        return HttpResponse("Invalid ID", status=400)

    # Get StudentManagerProfile instance
    student_manager_profile = get_object_or_404(StudentManagerProfile, user_id=id)
    user = student_manager_profile.user  # Get related User from the User model

    institutes = Institute.objects.filter(deleted_at__isnull=True)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        institute_id = request.POST.get('institute_id')
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        # Validation
        if not first_name:
            errors['first_name'] = "First Name is required."
        if not last_name:
            errors['last_name'] = "Last Name is required."
        if not email:
            errors['email'] = "Email is required."
        if not institute_id:
            errors['institute_id'] = "Institute is required."
            
        if password:
            if len(password) < 8:
                errors['password'] = "Password must be at least 8 characters long."
            if not re.search(r'[A-Z]', password):
                errors['password'] = "Password must contain at least one uppercase letter."
            if not re.search(r'[a-z]', password):
                errors['password'] = "Password must contain at least one lowercase letter."
            if not re.search(r'\d', password):
                errors['password'] = "Password must contain at least one digit."
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors['password'] = "Password must contain at least one special character."
            if password != confirm_password:
                errors['confirm_password'] = "Passwords do not match."

        if errors:
            return render(request, 'student_manager/student_manager_update.html', {
                'student_manager': student_manager_profile,
                'user': user,  # Pass the user separately
                'institutes': institutes,
                'errors': errors
            })

        try:
            with transaction.atomic():
                # Update User model
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = email  # Ensuring username is updated
                user.save()

                # Update StudentManagerProfile model
                institute = get_object_or_404(Institute, id=institute_id)
                student_manager_profile.institute_id = institute
                student_manager_profile.save()
                
                if password:
                    user.password = make_password(password)
                    user.save()

            messages.success(request, "Student Manager updated successfully!")
            return redirect('student_managers')

        except Exception as e:
            messages.error(request, f"An error occurred while updating the student manager: {e}")

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Student Managers", "url": reverse('student_managers')},
        {"name": "Student Manager Update", "url": ""},
    ]

    return render(request, 'student_manager/student_manager_update.html', {
        'student_manager': student_manager_profile,
        'user': user,  # Pass the user separately
        'institutes': institutes,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    })



def student_manager_delete(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    try:
        with transaction.atomic():  # Ensures all deletions happen together
            # Fetch user
            user = get_object_or_404(User, id=id)

            # Delete related records
            UserRoles.objects.filter(user=user).delete()
            StudentManagerProfile.objects.filter(user=user).delete()

            # Finally, delete the user itself
            user.delete()

            messages.success(request, "Student Manager deleted successfully!")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the student manager: {e}")

    return redirect('student_managers')



def student_list_by_manager(request, id):
    # Decode the ID (if it's encoded)
    manager_id = base64_decode(id)

    # Get the Student Manager
    student_manager = get_object_or_404(User, id=manager_id)

    # Fetch students where student_manager_email matches the Student Manager's email
    students = Students.objects.filter(student_manager_email=student_manager.email)
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
                'intake_year': getattr(student, 'intake_year', '') or '',
                'intake_month': getattr(student, 'intake_month', '') or '',
                'zoho_lead_id': getattr(student, 'zoho_lead_id', '') or '',
            }
            for student in queryset
        ]

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Student Managers", "url": reverse('student_managers')},
        {
            "name": f"Students Managed by - {student_manager.first_name} {student_manager.last_name}" if student_manager else "Unknown",
            "url": "",
        }
    ]

    return render(request, 'student_manager/student_list.html', {
        "student_manager": student_manager,
        'all_students': format_student_data(students),
        'verified_students': format_student_data(verified_students),
        'rejected_students': format_student_data(rejected_students),
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    })
