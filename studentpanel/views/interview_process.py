from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from flask import Flask, request, jsonify
import os
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import CommonQuestion
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# from .serializers import QuestionSerializer
# from .serializers import QuestionSerializer
def interview_start(request):
    return render(request, "index.html")


def interview_panel(request):
    return render(request, "interview-panel.html")


def interview_score(request):
    return render(request, "interview-score.html")


def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.STUDENT_UPLOAD, 'uploads/student_interview/')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path
# app = Flask(__name__)
# @app.route('/interveiw-section/interview_video_upload',methods=['POST'])
@csrf_exempt
def interview_video_upload(request):
    # print(r"test")
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        file_path = handle_uploaded_file(file)
        return JsonResponse({'message': 'File successfully uploaded', 'file_path': file_path})
    else:
        return JsonResponse({'error': 'No file part in the request'}, status=400)



# @csrf_exempt
# def interview_questions(request):
#     if request.method == 'POST' and 'file' in request.FILES:
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(file.name, file)
#         return JsonResponse({'message': 'File uploaded successfully', 'filename': filename}, status=200)
#     else:
#         return JsonResponse({'error': 'No file psddfsd'},status=500)

# def index(request):
#     return render('http://localhost:3000/home')

@csrf_exempt
def interview_questions(request):
    try:
        questions = CommonQuestion.objects.all()
        question_data = [
            {
                'question': question.question,
                'answer': question.answer,
                'encoded_id': question.id
            }
            for question in questions
        ]
        return JsonResponse({'questions': question_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

