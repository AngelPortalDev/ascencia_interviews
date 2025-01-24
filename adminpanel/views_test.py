from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *


def index(request):
    return render(request, "index.html")

def userdashboard(request):
    return render(request, "userdashboard.html")

def admindashboard(request):
    return render(request, "admindashboard.html")
