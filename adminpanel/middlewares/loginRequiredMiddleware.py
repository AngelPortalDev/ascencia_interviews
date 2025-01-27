from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define a list of path prefixes for which login is required
        login_required_prefixes = [
            '/adminpanel',
        ]

        # Define the login URL
        login_url = '/login/'  # Change this if your login page is different

        # Check if the user is authenticated and if the request path starts with any of the prefixes
        if not request.user.is_authenticated and any(request.path.startswith(prefix) for prefix in login_required_prefixes):
            # If not authenticated, redirect to the login page
            return redirect(f"{login_url}?next={request.path}")

        # Proceed to the next middleware or view
        return self.get_response(request)
