from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, "index.html")
def login_view(request):
    # If the user is already authenticated, redirect to the index page
    if request.user.is_authenticated:
        return redirect('admindashboard')

    # If the request method is POST, authenticate the user
    if request.method == 'POST':
        email = request.POST['email']  # Get the email from the form
        password = request.POST['password']  # Get the password from the form

        # Authenticate user using the email (lookup user by email)
        try:
            user = User.objects.get(email=email)  # Find the user by email
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        # If user is authenticated, log them in
        if user is not None:
            login(request, user)
            return redirect('admindashboard')  # Redirect to the index page
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login') 
        
    return render(request, 'auth/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/admindashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Validate the form inputs
        if not username or not password or not email:
            messages.error(request, 'All fields are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login') 
        
    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')
