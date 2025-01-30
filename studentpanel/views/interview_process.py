from django.http import HttpResponse
from django.shortcuts import render


def interview_start(request):
    return render(request, "interview-start.html")


def interview_panel(request):
    return render(request, "interview-panel.html")


def interview_score(request):
    return render(request, "interview-score.html")
