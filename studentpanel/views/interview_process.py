from django.http import HttpResponse
from django.shortcuts import render
from flask import Flask, request, jsonify
import os
from django.views.decorators.csrf import csrf_exempt


def interview_start(request):
    return render(request, "index.html")


def interview_panel(request):
    return render(request, "interview-panel.html")


def interview_score(request):
    return render(request, "interview-score.html")

@csrf_exempt
def interview_video_upload(request):
    print(request)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully'}), 200


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
