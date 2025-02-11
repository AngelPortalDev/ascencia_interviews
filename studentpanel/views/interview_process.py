from django.http import HttpResponse
from django.shortcuts import render


def interview_start(request):
    return render(request, "index.html")


def interview_panel(request):
    return render(request, "interview-panel.html")


def interview_score(request):
    return render(request, "interview-score.html")


# def index(request):
#     return render('http://localhost:3000/home')
