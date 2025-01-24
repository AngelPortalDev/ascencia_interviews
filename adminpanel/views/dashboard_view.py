from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


# def index(request):
#     return render(request, "index.html")

# def userdashboard(request):
#     return render(request, "userdashboard.html")

@login_required
def admindashboard(request):
    return render(request, "admindashboard.html")
