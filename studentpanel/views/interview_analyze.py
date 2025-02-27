import os
import json
import time
import subprocess
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from moviepy.video.io.VideoFileClip import VideoFileClip
from vosk import Model, KaldiRecognizer
from textblob import TextBlob
import wave
import speech_recognition as sr
from langdetect import detect
from googletrans import Translator
from adminpanel.common_imports import CommonQuestion
import re
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from gpt4all import GPT4All
# ✅ Paths (Update as per your system)
FFMPEG_PATH = r"C:\ffmpeg-2025-02-20-git-bc1a3bfd2c-full_build\bin\ffmpeg.exe"
# VOSK_MODEL_PATH = r"C:\Users\angel\Downloads\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"

# ✅ Initialize Vosk Model
# def initialize_vosk_model():
#     if not os.path.exists(VOSK_MODEL_PATH):
#         raise Exception("Vosk model not found!")
#     return Model(VOSK_MODEL_PATH)

# vosk_model = initialize_vosk_model()

# ✅ Handle File Upload
# def handle_uploaded_file(f):
#     upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "student_interview")
#     os.makedirs(upload_dir, exist_ok=True)
#     file_path = os.path.join(upload_dir, f.name)
#     with open(file_path, 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
#     return file_path

# ✅ Extract & Enhance Audio
def extract_audio(video_path):
    base_name = os.path.splitext(video_path)[0]
    audio_path = f"{base_name}.wav"
    enhanced_audio_path = f"{base_name}_enhanced.wav"

    try:
        # Extract audio using FFmpeg
        extract_cmd = [FFMPEG_PATH, "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path]
        subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Enhance audio (optional - noise reduction)
        enhance_cmd = [FFMPEG_PATH, "-i", audio_path, "-af", "highpass=f=200, lowpass=f=3000", enhanced_audio_path]
        subprocess.run(enhance_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return enhanced_audio_path

    except subprocess.CalledProcessError as e:
        print(f"Error processing audio: {e}")
        return None
# def extract_audio(video_path, audio_path):
#     """
#     Extracts audio from a video file using FFmpeg.
#     """
#     try:
#         ffmpeg.input(video_path).output(audio_path).run(overwrite_output=True)
#         return audio_path
#     except Exception as e:
#         print("Error extracting audio:", e)
#         return None

# def transcribe_audio(audio_path):
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(audio_path) as source:
#         audio_data = recognizer.record(source)
#         try:
#             return recognizer.recognize_google(audio_data)
#         except sr.UnknownValueError:
#             return "Could not understand audio"
#         except sr.RequestError:
#             return "Error with speech recognition service"

def check_grammar(text):
    detected_language = detect(text)
    if detected_language != 'en':
        return {
            "original_text": text,
            "corrected_text": text,  # No correction for non-English text
            "grammar_accuracy": 0
        }

    # Grammar check for English
    blob = TextBlob(text)
    corrected_text = str(blob.correct())
    
    original_words = text.split()
    corrected_words = corrected_text.split()

    correct_count = sum(1 for orig, corr in zip(original_words, corrected_words) if orig == corr)
    total_words = len(original_words)
    raw_accuracy = (correct_count / total_words) * 100 if total_words > 0 else 0

    # Scale grammar accuracy between 10 and 100
    grammar_accuracy = max(10, min(100, raw_accuracy))

    return {
        "original_text": text,
        "corrected_text": corrected_text,
        "grammar_accuracy": round(grammar_accuracy, 2)
    }
# ✅ Speech-to-Text (First 2 Minutes)
# def transcribe_audio(audio_path):
#     recognizer = KaldiRecognizer(vosk_model, 16000)  # 16kHz sample rate

#     with open(audio_path, "rb") as audio_file:
#         audio_data = audio_file.read()
#         recognizer.AcceptWaveform(audio_data)
    
#     result = json.loads(recognizer.Result())
#     return result.get("text", "")
# def transcribe_audio(audio_file):
#     wf = wave.open(audio_file, "rb")
#     rec = KaldiRecognizer(vosk_model, wf.getframerate())

#     transcription = []
#     while True:
#         data = wf.readframes(4000)
#         if len(data) == 0:
#             break
#         if rec.AcceptWaveform(data):
#             result = json.loads(rec.Result())
#             transcription.append(result.get("text", ""))

#     # Get final transcription text
#     final_result = json.loads(rec.FinalResult())
#     transcription.append(final_result.get("text", ""))

#     return " ".join(transcription)

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Error with speech recognition service"

# ✅ Sentiment Analysis
# def analyze_sentiment(transcribed_text):
#     blob = TextBlob(transcribed_text)
#     sentiment_score = blob.sentiment.polarity
#     print(sentiment_score)
#     if sentiment_score > 0:
#         return "Positive"
#     elif sentiment_score < 0:
#         return "Negative"
#     else:
#         return "Neutral"
def analyze_sentiment(text):
    detected_language = detect(text)
    
    
    # If the language is not English, translate it
    if detected_language != 'en':
        translator = Translator()
        translated = translator.translate(text, src=detected_language, dest='en')
        text = translated.text
    sentiment = TextBlob(text).sentiment

    if sentiment.polarity > 0:
        sentiment_label = "Positive"
    elif sentiment.polarity < 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
    return {
        "polarity": sentiment.polarity,  # -1 (negative) to 1 (positive)
        "subjectivity": sentiment.subjectivity,  # 0 (objective) to 1 (subjective),
        "sentiment": sentiment_label
    }


# ✅ Django View (API Endpoint)
@csrf_exempt
def analyze_video(request):
    if request.method == 'POST':
        data = request.POST
        video_path = data.get('video_path')
        audio_path = data.get('audio_path')
        # Extract audio
        extracted_audio = extract_audio(video_path)
        if not extracted_audio:
            return JsonResponse({"error": "Audio extraction failed"}, status=500)

        try:
            transcribed_text = transcribe_audio(extracted_audio)
            sentiment_analysis = analyze_sentiment(transcribed_text)
            grammar_results = check_grammar(transcribed_text)

            return JsonResponse({
                "transcription": transcribed_text,
                "sentiment": sentiment_analysis,
                "grammar_results": grammar_results,
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({"error": "Processing failed", "details": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


# Load BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_sentence_embedding(sentence):
    inputs = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the [CLS] token embedding
    return outputs.last_hidden_state[:, 0, :].numpy()
@csrf_exempt
def check_answers(request):
    start_time = time.time()  # Start timing
    data = request.POST
    answer = data.get("answer", "").strip()
    question_id = data.get("question_id")  # Assuming question ID contains the actual question
    student_id = data.get("student_id") # Get the logged-in student's ID

    if not question_id or not answer or not student_id:
        return JsonResponse({"error": "Question and answer and students are required."}, status=400)


    question_data = CommonQuestion.objects.get(id=question_id)

    # enrolled_courses = get_student_details(student_id)
    # print(enrolled_courses)
    # if not enrolled_courses:
    #     return JsonResponse({"error": "No enrolled courses found for the student."}, status=400)
    # 🔥 Enhanced prompt with logical consistency check
    prompt = f"""
    You are an AI evaluator for university applications.  
    Your task is to **evaluate answers based on meaning, not just grammar.**  

    **Evaluation Criteria:**
    1️⃣ **Relevance to the question** (Is the answer actually about the program?)  
    2️⃣ **Logical correctness** (Does the explanation make sense?)  
    3️⃣ **Grammar & clarity** (Is the sentence well-structured?)  

    **Scoring Rules:**  
    - **1-2/10** → Completely incorrect or unrelated (e.g., AI research for a Psychology degree).  
    - **3-5/10** → Somewhat related but logically weak.  
    - **6-8/10** → Relevant but lacks details.  
    - **9-10/10** → Strong, detailed, and logical answer.  

    **Example of a bad answer (Wrong Logic):**
    Question: "Why do you want to study Psychology?"  
    Answer: "I want to study Psychology because I love coding and want to build AI systems."  
    **Score: 1/10 (Completely incorrect - AI is not related to Psychology).**

    **Example of a good answer (Correct Logic):**
    Question: "Why do you want to study Psychology?"  
    Answer: "I am fascinated by human behavior and want to specialize in Cognitive Psychology to understand how people think."  
    **Score: 9/10 (Relevant, clear, and logical).**

    Now, evaluate the following answer:  
    **Question:** {question_data.question}  
    **Answer:** {answer}  

    Provide a score out of 10 and feedback in this format:  
    **Score: X/10**  
    **Feedback: [Your analysis]**  
    """

    try:
        model_path = r"C:\Users\angel\Ascencia_Interviews\ascencia_interviews\studentpanel\models\mistral-7b-instruct-v0.2.Q2_K.gguf"
        
        print("Loading model...")  # Debugging
        model = GPT4All(model_path)
        print("Model loaded successfully!")  # Debugging

        response = model.generate(prompt)
        print("AI Response:", response)  # Debugging

        # Improved regex to extract score
        match = re.search(r"Score:\s*(\d{1,2})\/10", response)
        score = int(match.group(1)) if match else None

        
        end_time = time.time()  # End timing
        response_time = round(end_time - start_time, 2)  # Calculate response time

        return JsonResponse({"score": score, "feedback": response, "response_time": f"{response_time} sec"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    # return enrolled_courses