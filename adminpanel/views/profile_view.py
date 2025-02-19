from adminpanel.common_imports import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import re


@login_required
def profile_update(request):
    user = request.user
    errors = {}

    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        first_name = request.POST.get("first_name").strip()
        last_name = request.POST.get("last_name").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()
        

        # Validate required fields
        if not username:
            errors['username'] = "Username is required."
        if not email:
            errors['email'] = "Email is required."

        # Check for duplicate username
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            errors['username'] = "This username is already taken."

        # Check for duplicate email
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            errors['email'] = "This email is already in use."

        # Validate password strength (if provided)
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
            return render(request, 'profile/profile_update.html', {'user': user, 'errors': errors})

        try:
            # Update user details
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name

            # Update password only if provided
            if password:
                user.password = make_password(password)

            user.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('profile_update')
            # return render(request, 'profile/profile_update.html', {'user': user, 'success_message': "Profile updated successfully!"})

        except Exception as e:
            # messages.error(request, f"An error occurred while updating your profile: {e}")
            messages.error(request, f"An error occurred: {e}")
            return redirect('profile_update')

            # return render(request, 'profile/profile_update.html', {'user': user, 'error_message': f"An error occurred: {e}"})
    return render(request, 'profile/profile_update.html', {'user': user})