from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, "index.html")


def institute_view(request):
    institutes = Institute.objects.all()
    return render(request, 'institute/institute.html', {'institutes': institutes})