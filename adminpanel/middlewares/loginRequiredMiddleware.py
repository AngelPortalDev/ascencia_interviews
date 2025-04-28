from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from django.shortcuts import render


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define a list of path prefixes for which login is required
        admin_only_paths = [
            '/adminpanel',
        ]
        student_manager_only_paths = [
            '/studentmanagerpanel',
        ]

        # Define the login URL
        login_url = '/login'  # Change this if your login page is different

        # Check if the user is authenticated and if the request path starts with any of the prefixes
        # if not request.user.is_authenticated and any(request.path.startswith(prefix) for prefix in login_required_prefixes):
        #     # If not authenticated, redirect to the login page
        #     return redirect(f"{login_url}?next={request.path}")
        
        # if request.user.is_authenticated and request.user.profile.role != 1:
        #     return HttpResponseNotFound(render(request, '401.html'))

        if not request.user.is_authenticated:
            if any(request.path.startswith(prefix) for prefix in admin_only_paths + student_manager_only_paths):
                return redirect(f"{login_url}?next={request.path}")

        # Restrict admin (role = 1) from accessing student manager panel
        if request.user.is_authenticated and request.user.profile.role == 0:
            if any(request.path.startswith(prefix) for prefix in student_manager_only_paths):
                return HttpResponseNotFound(render(request, '401.html'))

        # Restrict student manager (role = 2) from accessing admin panel
        if request.user.is_authenticated and request.user.profile.role == 1:
            if any(request.path.startswith(prefix) for prefix in admin_only_paths):
                return HttpResponseNotFound(render(request, '401.html'))

        # Proceed with the request
        return self.get_response(request)
