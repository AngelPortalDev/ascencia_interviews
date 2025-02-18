from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from flask import Flask, request, jsonify
import os
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import CommonQuestion
# from .serializers import QuestionSerializer
# from .serializers import QuestionSerializer
def interview_start(request):
    return render(request, "index.html")


def interview_panel(request):
    return render(request, "interview-panel.html")


def interview_score(request):
    return render(request, "interview-score.html")

# app = Flask(__name__)
# @app.route('/interveiw-section/interview_video_upload',methods=['POST'])
@csrf_exempt
def interview_video_upload(request):
    print(r"test")
    # if 'file' not in request.files:
    #     return jsonify({'error': 'No file part in the request'}), 400
    # file = request.files['file']
    # if file.filename == '':
    #     return jsonify({'error': 'No selected file'}), 400
    # filename = secure_filename(file.filename)
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # return jsonify({'message': 'File uploaded successfully'}), 200


def interview_questions(request):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully'}), 200
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
                # 'encoded_id': base64_encode(question.id)
            }
            for question in questions
        ]
        return JsonResponse({'questions': question_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


