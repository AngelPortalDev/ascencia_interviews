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
import cv2
import numpy as np
import subprocess
import requests
from studentpanel.models.interview_process_model import Students




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






# def convert_to_webm(video_path, output_path):
#     """ Converts a video to WebM format using VP9 codec. """
#     command = f'ffmpeg -i "{video_path}" -c:v libvpx-vp9 -b:v 1M -c:a libopus "{output_path}"'
#     subprocess.run(command, shell=True, check=True)

# def merge_videos(uploads_folder, video_files, output_filename="merged_video.webm"):
#     # video_files = ["1.webm", "2.webm"] 
#     converted_files = []
#     list_file_path = os.path.join(uploads_folder, "video_list.txt").replace("\\", "/")

#     # Convert all videos to WebM format
#     for video in video_files:
#         input_path = os.path.join(uploads_folder, video).replace("\\", "/")
#         if not os.path.exists(input_path):
#             return f"Error: {video} not found in uploads folder."

#         output_path = os.path.join(uploads_folder, f"{os.path.splitext(video)[0]}_converted.webm").replace("\\", "/")
#         convert_to_webm(input_path, output_path)
#         converted_files.append(output_path)

#     # Create video list file
#     with open(list_file_path, "w") as f:
#         for video in converted_files:
#             f.write(f"file '{video}'\n")

#     # Define output path
#     output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")

#     # Merge converted WebM files
#     command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c copy "{output_path}"'
    
#     try:
#         subprocess.run(command, shell=True, check=True)
#         return f"Merged video saved at: {output_path}"
#     except subprocess.CalledProcessError as e:
#         return f"Error merging videos: {e}"

# # Example usage
# zoho_lead_id = '787878'
# video_files = ["1.webm", "2.webm"] 
# uploads_folder = "C:/xampp/htdocs/ascencia_interviews/uploads/787878"
# print(merge_videos(uploads_folder, video_files))












def upload_to_bunnystream(video_path):
    BUNNY_STREAM_LIBRARY_KEY = "e31364b4-b2f4-4221-aac3bd5d34e5-6769-4f29"  # Replace with your actual Library Key
    BUNNY_STREAM_LIBRARY_ID = "390607"  # Replace with your actual Library ID

    """Uploads a compressed video to BunnyStream and returns the video URL."""
    print("Video Path:", video_path)
    video_name = os.path.basename(video_path)

    # 1. Create Video Entry
    create_url = f"https://video.bunnycdn.com/library/{BUNNY_STREAM_LIBRARY_ID}/videos"
    headers = {
        "AccessKey": BUNNY_STREAM_LIBRARY_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(create_url, json={"title": video_name}, headers=headers)
    # print("Create Response:", response.status_code, response.text)

    # if response.status_code != 201:
    #     return f"Error creating video entry: {response.text}"

    video_id = response.json().get("guid")
    if not video_id:
        return "Error: Video GUID not received."

    # 2. Upload Video File (Corrected URL & Headers)
    upload_url = f"https://video.bunnycdn.com/library/{BUNNY_STREAM_LIBRARY_ID}/videos/{video_id}"
    headers = {
        "AccessKey": BUNNY_STREAM_LIBRARY_KEY,
        "Content-Type": "application/octet-stream"
    }

    with open(video_path, "rb") as video_file:
        upload_response = requests.put(upload_url, headers=headers, data=video_file)
        return video_id
        
    print("Upload Response:", upload_response.status_code, upload_response.text)

    if upload_response.status_code != 201:  # BunnyStream returns 201 for success
        return f"Error uploading video: {upload_response.text}"

    return f"https://iframe.mediadelivery.net/embed/{BUNNY_STREAM_LIBRARY_ID}/{video_id}"





def compress_video(input_path, output_path, target_size_mb=19):
    """Compresses a video to fit within the specified size limit."""
    target_size = target_size_mb * 1024 * 1024  # Convert MB to bytes

    # Get the original file size
    original_size = os.path.getsize(input_path)

    if original_size <= target_size:
        return f"Compression not needed, size: {original_size / (1024 * 1024):.2f} MB"

    # Compression settings
    bitrate = (target_size * 8) / os.path.getmtime(input_path)  # Approximate bitrate calculation
    compressed_output = os.path.splitext(output_path)[0] + "_compressed.mp4"

    compress_command = (
        f'ffmpeg -i "{input_path}" -b:v {bitrate} -c:v libx264 -preset fast '
        f'-c:a aac -b:a 128k -movflags +faststart "{compressed_output}"'
    )

    try:
        subprocess.run(compress_command, shell=True, check=True)
        return f"Compressed video saved at: {compressed_output}"
    except subprocess.CalledProcessError as e:
        return f"Error compressing video: {e}"



def convert_video(input_path, output_path, target_format):
    """ Converts a video to the specified format with correct encoding. """
    if target_format == "webm":
        command = f'ffmpeg -i "{input_path}" -c:v libvpx-vp9 -b:v 1M -c:a libopus "{output_path}"'
    elif target_format == "mp4":
        command = f'ffmpeg -i "{input_path}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
    elif target_format == "mov":
        command = f'ffmpeg -i "{input_path}" -c:v prores -c:a pcm_s16le "{output_path}"'
    else:
        return f"Unsupported format: {target_format}"

    subprocess.run(command, shell=True, check=True)



def get_uploads_folder():
    """Returns the absolute path to the 'uploads' folder in the project root."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # Go two levels up
    uploads_folder = os.path.join(project_root, "uploads")  # Point to the correct uploads folder
    return uploads_folder.replace("\\", "/")  # Normalize path


def merge_videos(zoho_lead_id, base_uploads_folder="C:/xampp/htdocs/ascencia_interviews/uploads"):
    """ Merges all videos in the lead's folder into a single file of the detected format. """
    # uploads_folder = os.path.join(base_uploads_folder, zoho_lead_id).replace("\\", "/")

    uploads_folder = os.path.join(get_uploads_folder(), zoho_lead_id)

    # Check if the folder exists
    if not os.path.exists(uploads_folder):
        return f"Error: Folder {uploads_folder} does not exist."

    video_files = [f for f in os.listdir(uploads_folder) if f.endswith((".webm", ".mp4", ".mov"))]
    
    if not video_files:
        return f"Error: No video files found in {uploads_folder}."

    # Detect the format from the first video file
    first_video_ext = os.path.splitext(video_files[0])[1][1:]  # Extract extension without the dot
    target_format = first_video_ext.lower()  # Normalize format (webm, mp4, mov)

    converted_files = []
    list_file_path = os.path.join(uploads_folder, "video_list.txt").replace("\\", "/")
    output_filename = f"merged_video.{target_format}"
    output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")

    # Convert all videos to the detected format
    for video in video_files:
        input_path = os.path.join(uploads_folder, video).replace("\\", "/")
        output_path_converted = os.path.join(uploads_folder, f"{os.path.splitext(video)[0]}_converted.{target_format}").replace("\\", "/")

        if not video.endswith(f".{target_format}"):  # Convert only if needed
            convert_video(input_path, output_path_converted, target_format)
            converted_files.append(output_path_converted)
        else:
            converted_files.append(input_path)

    # Create video list file
    with open(list_file_path, "w") as f:
        for video in converted_files:
            f.write(f"file '{video}'\n")

    # Select correct encoding based on target format
    if target_format == "webm":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c:v libvpx-vp9 -b:v 1M -c:a libopus "{output_path}"'
    elif target_format == "mp4":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -map 0:v -map 0:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
    elif target_format == "mov":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c:v prores -c:a pcm_s16le "{output_path}"'
    else:
        return f"Unsupported format: {target_format}"

    # Merge videos with re-encoding
    try:
        subprocess.run(merge_command, shell=True, check=True)
        # Check size and compress if needed
        # if os.path.getsize(output_path) > (19 * 1024 * 1024):
        #     return compress_video(output_path, output_path)

        video_id = upload_to_bunnystream(output_path)

        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        student.bunny_stream_video_id = video_id
        student.save()
        return f"video_id: {video_id}"  
        return f"Merged video saved at: {output_path}"  
    except subprocess.CalledProcessError as e:
        return f"Error merging videos: {e}"
    
# Example usage
# zoho_lead_id = "5204268000112707003"
# print(merge_videos(zoho_lead_id))





def delete_video(request, student_id):
    BUNNY_STREAM_API_KEY = "e31364b4-b2f4-4221-aac3bd5d34e5-6769-4f29"  # Replace with your actual Library Key
    BUNNY_STREAM_LIBRARY_ID = "390607"
    if request.method == "POST":
        try:
            student = Students.objects.get(id=student_id)
            video_id = student.bunny_stream_video_id
            
            if not video_id:
                return JsonResponse({"success": False, "message": "No video ID found!"})

            # BunnyStream API Call to Delete Video
            delete_url = f"https://video.bunnycdn.com/library/{BUNNY_STREAM_LIBRARY_ID}/videos/{video_id}"
            headers = {"AccessKey": BUNNY_STREAM_API_KEY}
            response = requests.delete(delete_url, headers=headers)
            print(r'status_code:', response.status_code)
            if response.status_code in [200, 204]:
                student.bunny_stream_video_id = None
                student.save()
                return JsonResponse({"success": True, "debug": "Delete API reached"}) 

            else:
                return JsonResponse({"success": False, "message": response.text})
        
        except Students.DoesNotExist:
            return JsonResponse({"success": False, "message": "Student not found!"})
    return JsonResponse({"success": False, "message": "Invalid request!"})