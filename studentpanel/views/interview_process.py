from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from flask import Flask, request, jsonify
import os
import base64
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from django.core.files.storage import FileSystemStorage
from studentpanel.models.student_interview_answer import StudentInterviewAnswers

from django.conf import settings
# from .serializers import QuestionSerializer
# from .serializers import QuestionSerializer
def interview_start(request):
    return render(request, "index.html")


def interview_panel(request):
    return render(request, "interview-panel.html")


def interview_score(request):
    return render(request, "interview-score.html")


def handle_uploaded_file(file,student_id):

    upload_dir = os.path.join(settings.STUDENT_UPLOAD, 'uploads', 'student_interview', student_id)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path
# app = Flask(__name__)
# @app.route('/interveiw-section/interview_video_upload',methods=['POST'])
@csrf_exempt
def interview_video_upload(request):
    # print(r"test")
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        student_id = request.POST.get('student_id')
        file_path = handle_uploaded_file(file,student_id)
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
                # 'answer': question.answer,
                'encoded_id': question.id
            }
            for question in questions
        ]
        return JsonResponse({'questions': question_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

    
@csrf_exempt
def student_data(request):
    if request.method == 'POST':
        data = request.POST
        student_id = data.get('student_id')
        if not student_id:
            return JsonResponse({"error": "student id does not exists"}, status=500)
    try:
        decoded_bytes = base64.b64decode(student_id)
        student_id = decoded_bytes.decode("utf-8")  # Convert bytes to string
        student = Students.objects.get(zoho_lead_id=student_id)
        student_data = [
            {
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email_id': student.email,
                'zoho_lead_id': student.zoho_lead_id,
                'mobile_no':student.phone
            }
        ]
        return JsonResponse({'student_data': student_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


@csrf_exempt
def student_interview_answers(request):
    # if request.method == 'POST':
    #     data = request.POST
    #     student_id = data.get('student_id')
    #     if not student_id:
    #         return JsonResponse({"error": "student id does not exists"}, status=500)
    # try:
    #     decoded_bytes = base64.b64decode(student_id)
    #     student_id = decoded_bytes.decode("utf-8")  # Convert bytes to string
    #     student = StudentInterviewAnswers.objects.get(zoho_lead_id=student_id)
    #     student_data = [
    #         {
    #             'first_name': student.first_name,
    #             'last_name': student.last_name,
    #             'email_id': student.email,
    #             'zoho_lead_id': student.zoho_lead_id,
    #             'mobile_no':student.phone
    #         }
    #     ]

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        zoho_lead_id = request.POST.get('zoho_lead_id')
        question_id = request.POST.get('question_id')
        answer_text = request.POST.get('answer_text')
        sentiment_score = request.POST.get('sentiment_score')
        # sent_subj = request.POST.get('sent_subj')

        grammar_accuracy = request.POST.get('grammar_accuracy')
        try:
            data_to_save = {
                'student_id': student_id,
                'zoho_lead_id': zoho_lead_id,
                'question_id': question_id,
                'answer_text': answer_text,
                'sentiment_score': sentiment_score,
                # 'sent_subj':"sdas",
                'grammar_accuracy': grammar_accuracy,
                'zoho_lead_id': zoho_lead_id
            }
            

            result = save_data(StudentInterviewAnswers, data_to_save)
            # print(r'result:', result)

            if result['status']:
                return JsonResponse({"status": True, "message": "Student updated successfully!"}, status=200)
            else:
                return JsonResponse({"status": False, "error": result.get('error', "Failed to update the student.")}, status=400)

        except Exception as e:
            return JsonResponse({"status": False, "error": str(e)}, status=500)

    return JsonResponse({"status": False, "error": "Invalid request method"}, status=405)