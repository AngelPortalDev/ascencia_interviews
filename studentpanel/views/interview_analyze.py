import os
import json
import time
import subprocess
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from vosk import Model, KaldiRecognizer
from textblob import TextBlob
# import wave
import speech_recognition as sr
from langdetect import detect
from googletrans import Translator
from adminpanel.common_imports import CommonQuestion
import re
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
# from gpt4all import GPT4All
import cv2
import numpy as np
import subprocess
import requests
import numpy as np
import base64
from studentpanel.models.interview_process_model import Students

from django.conf import settings
from adminpanel.utils import send_email
import logging
from collections import defaultdict
from studentpanel.models.student_interview_answer import StudentInterviewAnswers
from studentpanel.models.interview_link import StudentInterviewLink
from decimal import Decimal
logger = logging.getLogger(__name__)
from django_q.tasks import async_task
from adminpanel.common_imports import save_data



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
    print(video_path)
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
def clean_polarity(value):
    try:
        # Convert to float and ensure it's within the valid range
        polarity = float(value)
        if polarity < -1.0:
            polarity = -1.0
        elif polarity > 1.0:
            polarity = 1.0
        return polarity
    except ValueError:
        return 0.0  # Default to neutral if conversion fails
    
def analyze_sentiment(text):
    detected_language = detect(text)
    
    # If the language is not English, translate it
    if detected_language != 'en':
        translator = Translator()
        translated = translator.translate(text, src=detected_language, dest='en')
        text = translated.text
    
    sentiment = TextBlob(text).sentiment
    subjectivity = sentiment.subjectivity  # Confidence estimate (0 to 1)
    confidence_level = (1 - subjectivity) * 100  # Higher objectivity = higher confidence
    polarity = clean_polarity(sentiment.polarity)
    # Convert polarity (-1 to 1) into a percentage (0 to 100)
    sentiment_score = (polarity + 1) * 50  

    return {
        "polarity": polarity,  # -1 (negative) to 1 (positive)
        "subjectivity": sentiment.subjectivity,  # 0 (objective) to 1 (subjective),
        "sentiment_score": round(sentiment_score, 2),  # 0 to 100% dynamically
        "confidence_level": round(confidence_level, 2),
    }

@csrf_exempt
def interview_add_video_path(request):
    if request.method == 'POST':
        data = request.POST
        video_path = data.get('video_path')
        # audio_path = data.get('audio_path')
        question_id = data.get('question_id')
        zoho_lead_id = data.get('zoho_lead_id')
        last_question_id=data.get('last_question_id')

        try:
            zoho_lead_id = base64.b64decode(zoho_lead_id).decode("utf-8")
            question_id = base64.b64decode(question_id).decode("utf-8")
            last_question_id = base64.b64decode(last_question_id).decode("utf-8")
            data_to_save = {
                'video_path': video_path,
                'question_id': question_id,
                'zoho_lead_id': zoho_lead_id,
            }
            
            result = save_data(StudentInterviewAnswers, data_to_save)
            async_task(analyze_video(video_path,question_id,zoho_lead_id,last_question_id))
            # print(r'result:', result)

            if result['status']:
                return JsonResponse({"status": True, "message": "Student updated successfully!"}, status=200)
            else:
                return JsonResponse({"status": False, "error": result.get('error', "Failed to update the student.")}, status=400)

        except Exception as e:
            return JsonResponse({"status": False, "error": str(e)}, status=500)

    return JsonResponse({"status": False, "error": "Invalid request method"}, status=405)


def student_interview_answers(zoho_lead_id, question_id, answer_text, sentiment_score, sent_subj, confidence_level, grammar_accuracy, last_question_id):
    try:
        data_to_save = {
            "zoho_lead_id": zoho_lead_id,
            "question_id": question_id,
            "answer_text": answer_text,
            "sentiment_score": sentiment_score,
            "sent_subj": sent_subj,
            "grammar_accuracy": grammar_accuracy,
            "confidence_level": confidence_level,
        }

        print("Saving data:", data_to_save)

        result = save_data(
            StudentInterviewAnswers,
            data_to_save,
            where={"zoho_lead_id": zoho_lead_id, "question_id": question_id},
        )

        if result["status"]:
            return {"status": True, "message": "Student updated successfully!"}
        else:
            return {"status": False, "error": result.get("error", "Failed to update the student.")}

    except Exception as e:
        return {"status": False, "error": str(e)}


# print(async_task(analyze_video("C:\\Users\\angel\\Ascencia_Interviews\\ascencia_interviews\\uploads\\interview_videos\\5204268000112707003\\interview_video_5204268000112707003_3_2025-03-05T07-29-27.webm", '1', '5204268000112707003', '5')))
    # return JsonResponse({"status": False, "error": "Invalid request method"}, status=405)
# def analyze_video(zoho_lead_id):
#     # if request.method == 'POST':
#         # data = request.POST
#         # video_path = data.get('video_path')
#         # # audio_path = data.get('audio_path')
#         # question_id = data.get('question_id')
#         # zoho_lead_id = data.get('zoho_lead_id')
#         # last_question_id=data.get('last_question_id')
#         # print("data",data)
#         # student_questions = {}  # Dictionary to store last question per student
#         print(zoho_lead_id)
        
#         try:
#             student_answers = StudentInterviewAnswers.objects.filter(zoho_lead_id=zoho_lead_id)

#             for student_answer in student_answers:
#                 zoho_lead_id = student_answer.zoho_lead_id
#                 video_path = student_answer.student_id
#                 question_id = student_answer.question_id

#             # Extract audio from video
#             extracted_audio = extract_audio(video_path)
#             if not extracted_audio:
#                 return JsonResponse({"error": "Audio extraction failed"}, status=500)

#             # Perform analysis
#             transcribed_text = transcribe_audio(extracted_audio)
#             sentiment_analysis = analyze_sentiment(transcribed_text)
#             grammar_results = check_grammar(transcribed_text)

#             # Check if the question is the last one
#             # if student_answers.exists():
#             #     last_question_id = student_answers.last().question_id  # Assuming `last_question_id` means the last stored question

#             #     if last_question_id == question_id:
#             #         async_task("studentpanel.views.interview_process.check_answers", zoho_lead_id)
#             #         async_task("studentpanel.views.interview_process.merge_videos", zoho_lead_id)
#             # student_interview_answers(student_id=123,zoho_lead_id,transcribed_text,sentiment_analysis.sentiment_score)
#             return JsonResponse({
#                 "transcription": transcribed_text,
#                 "sentiment": sentiment_analysis,
#                 "grammar_results": grammar_results,
#                 "status": "success",
#                 "question_id": question_id,
#                 "zoho_lead_id": zoho_lead_id,
#             })

#         except Exception as e:
#             return JsonResponse({"error": "Processing failed", "details": str(e)}, status=500)

#     # return JsonResponse({"error": "Invalid request"}, status=400)

# Load BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_sentence_embedding(sentence):
    inputs = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the [CLS] token embedding
    return outputs.last_hidden_state[:, 0, :].numpy()
# @csrf_exempt
def check_answers(zoho_lead_id):
    print(f"Processing lead ID: {zoho_lead_id}")  # Debugging

    student_answers = StudentInterviewAnswers.objects.filter(zoho_lead_id=zoho_lead_id)

    if not student_answers.exists():
        logger.info("No student records found.")
        return

    model_path = "C:/Users/angel/Ascencia_Interviews/ascencia_interviews/studentpanel/models/mistral-7b-instruct-v0.2.Q2_K.gguf"

    # ✅ Check if AI model file exists
    if not os.path.exists(model_path):
        logger.error("AI model path does not exist.")
        return

    final_results = []

    try:
        logger.info("Loading AI Model...")
        model = GPT4All(model_path)
        logger.info("Model loaded successfully!")

        # Dictionaries for storing scores
        student_scores = defaultdict(int)
        student_question_count = defaultdict(int)
        student_sentiment = defaultdict(float)
        student_grammar = defaultdict(float)

        # Fetch all questions in a single query
        question_map = {q.id: q for q in CommonQuestion.objects.all()}

        for student_answer in student_answers:
            zoho_lead_id = student_answer.zoho_lead_id
            question_id = student_answer.question_id
            answer = student_answer.answer_text.strip() if student_answer.answer_text else ""
            sentiment_score = float(student_answer.sentiment_score) if student_answer.sentiment_score else 0.0
            grammar_accuracy = float(student_answer.grammar_accuracy) if student_answer.grammar_accuracy else 0.0

            # Debugging: Print Sentiment Score
            print(f"Processing {zoho_lead_id} - Q{question_id} - Sentiment: {sentiment_score}, Grammar: {grammar_accuracy}")

            if not zoho_lead_id or not question_id or not answer:
                logger.warning(f"Skipping: Missing data for Lead {zoho_lead_id}, Q{question_id}")
                continue

            student_question_count[zoho_lead_id] += 1  

            if question_id not in question_map:
                logger.warning(f"Question ID {question_id} not found in database.")
                continue

            question_data = question_map[question_id]

            student_sentiment[zoho_lead_id] += sentiment_score
            student_grammar[zoho_lead_id] += grammar_accuracy

            print(f"Updated Scores - Lead {zoho_lead_id}: Sentiment={student_sentiment[zoho_lead_id]}, Grammar={student_grammar[zoho_lead_id]}")


            # 🔹 Check Student Name for Question ID 1
            if question_id == 1:
                possible_names = re.findall(r'\b[A-Z][a-z]*\b', answer)
                student_data = Students.objects.filter(zoho_lead_id=zoho_lead_id).values("first_name").first()
                if student_data:
                    actual_first_name = student_data["first_name"]
                    if actual_first_name not in possible_names:
                        final_results.append({
                            "zoho_lead_id": zoho_lead_id,
                            "question_id": question_id,
                            "total_questions": student_question_count[zoho_lead_id],
                            "overall_score": student_scores[zoho_lead_id],
                            "status": "No matching name found",
                        })
                        continue  

            # 🔹 Check Program Name for Question ID 2
            if question_id == 2:
                student_program = Students.objects.filter(zoho_lead_id=zoho_lead_id).values("program").first()
                if student_program:
                    program_name = student_program["program"].strip()
                    if not re.search(rf"\b{re.escape(program_name)}\b", answer, re.IGNORECASE):
                        final_results.append({
                            "zoho_lead_id": zoho_lead_id,
                            "question_id": question_id,
                            "total_questions": student_question_count[zoho_lead_id],
                            "overall_score": student_scores[zoho_lead_id],
                            "status": "Program name mismatch",
                        })
                        continue

            # ✅ AI Evaluation Prompt
            prompt = f"""
            You are an AI evaluator for university applications.  
            Your task is to **evaluate answers based on meaning, not just grammar.**  

            **Evaluation Criteria:**
            1️⃣ **Relevance to the question**  
            2️⃣ **Logical correctness**  
            3️⃣ **Grammar & clarity**  

            **Scoring Rules:**  
            - **1-2/10** → Completely incorrect or unrelated.  
            - **3-5/10** → Somewhat related but logically weak.  
            - **6-8/10** → Relevant but lacks details.  
            - **9-10/10** → Strong, detailed, and logical answer.  

            Now, evaluate the following answer:  
            **Question:** {question_data.question}  
            **Answer:** {answer}  

            Provide a score out of 10 and feedback in this format:  
            **Score: X/10**  
            **Feedback: [Your analysis]**  
            """

            try:
                start_time = time.time()
                response = model.generate(prompt)
                end_time = time.time()
                response_time = round(end_time - start_time, 2)

                # 🔹 Extract score safely
                match = re.search(r"Score:\s*(\d+)/10", response)
                score = int(match.group(1)) if match else 0

                # Store scores
                student_scores[zoho_lead_id] += score  
            
            except Exception as ai_error:
                logger.error(f"AI model evaluation error: {ai_error}")
                continue

          
        # # ✅ Prepare final results
        for zoho_lead_id in student_scores.keys():
            total_questions = student_question_count[zoho_lead_id]
            total_score = student_scores[zoho_lead_id]

            answer_score_percentage = 100 * (total_score) / (total_questions * 10) if total_questions else 0
            sentiment_score_percentage = 100 * (student_sentiment[zoho_lead_id]) / (total_questions * 100) if total_questions else 0
            grammar_accuracy_percentage = 100 * (student_grammar[zoho_lead_id]) / (total_questions * 100) if total_questions else 0

            final_results.append({
                "zoho_lead_id": zoho_lead_id,
                "total_score": total_score,  
                "total_questions": total_questions,
                "answer_score_percentage": answer_score_percentage,
                "sentiment_score_percentage": sentiment_score_percentage,
                "grammar_accuracy_percentage": grammar_accuracy_percentage
            })

            overall_score = (answer_score_percentage+sentiment_score_percentage+grammar_accuracy_percentage) * 100 / 300
            if grammar_accuracy_percentage > 20:
                status = "Pass" if overall_score >= 35 else "Fail"
            else:
                status = "Fail"  # Default Fail if grammar score <= 20

            data_to_save = {
                "overall_score": Decimal(overall_score),  # Ensure correct type
                "total_answer_scores":Decimal(answer_score_percentage),
                "total_grammar_scores":Decimal(grammar_accuracy_percentage),
                "total_sentiment_score":Decimal(sentiment_score_percentage),
                "interview_status":status
            }
            updated_count = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id).update(**data_to_save)

            # print(data_to_save)
            # updated_count = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id).update(**data_to_save)
            # updated_count = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id).update(**data_to_save)
            # print(updated_count)
            if(updated_count == 1):
                 return {"status": True, "message": "Student Interview Answer updated successfully!"}
            logger.info(f"Final Results: {final_results}")
            # logger.info(f"Saved Data: {result}")

    except Exception as e:
        logger.error(f"Error in AI evaluation: {e}")







def upload_to_bunnystream(video_path):
    # BUNNY_STREAM_API_KEY = "e31364b4-b2f4-4221-aac3bd5d34e5-6769-4f29"  # Replace with your actual Library Key
    # BUNNY_STREAM_LIBRARY_ID = "390607"  # Replace with your actual Library ID

    """Uploads a compressed video to BunnyStream and returns the video URL."""
    # print("Video Path:", video_path)
    video_name = os.path.basename(video_path)

    # 1. Create Video Entry
    create_url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos"
    headers = {
        "AccessKey": settings.BUNNY_STREAM_API_KEY,
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
    upload_url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos/{video_id}"
    headers = {
        "AccessKey": settings.BUNNY_STREAM_API_KEY,
        "Content-Type": "application/octet-stream"
    }

    with open(video_path, "rb") as video_file:
        upload_response = requests.put(upload_url, headers=headers, data=video_file)
        return video_id
        
    print("Upload Response:", upload_response.status_code, upload_response.text)

    if upload_response.status_code != 201:  # BunnyStream returns 201 for success
        return f"Error uploading video: {upload_response.text}"

    return f"https://iframe.mediadelivery.net/embed/{settings.BUNNY_STREAM_LIBRARY_ID}/{video_id}"





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
    uploads_folder = os.path.join(project_root, "uploads/interview_videos")  # Point to the correct uploads folder
    return uploads_folder.replace("\\", "/")  # Normalize path


def merge_videos(zoho_lead_id, base_uploads_folder="C:/xampp/htdocs/ascencia_interviews/uploads/interview_videos"):
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
        
        url = f"{settings.ADMIN_BASE_URL}/adminpanel/student/{zoho_lead_id}/"
        # student manager
        send_email(
            subject="Interview Process Completed",
            message=f"""
                    <html>
                    <body>
                        <p>Lead update was successful.</p>
                        <p>The interview process is completed. Please review the video here:</p>
                        <p><a href='{url}'>Check Interview Video</a></p>
                    </body>
                    </html>
                """,
            recipient=["abdullah@angel-portal.com"],
            # cc=["admin@example.com", "hr@example.com"]  # CC recipients
        )
        return f"video_id: {video_id}"  
        return f"Merged video saved at: {output_path}"  
    except subprocess.CalledProcessError as e:
        return f"Error merging videos: {e}"
    
# Example usage
# zoho_lead_id = "5204268000112707003"
# print(merge_videos(zoho_lead_id))

def delete_video(request, zoho_lead_id):
    # BUNNY_STREAM_API_KEY = "e31364b4-b2f4-4221-aac3bd5d34e5-6769-4f29"  # Replace with your actual Library Key
    # BUNNY_STREAM_LIBRARY_ID = "390607"
    if request.method == "POST":
        try:
            student = Students.objects.get(id=zoho_lead_id)
            video_id = student.bunny_stream_video_id
            
            if not video_id:
                return JsonResponse({"success": False, "message": "No video ID found!"})

            # BunnyStream API Call to Delete Video
            delete_url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos/{video_id}"
            headers = {"AccessKey": settings.BUNNY_STREAM_API_KEY}
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


@csrf_exempt
def analyze_video(video_path,question_id,zoho_lead_id,last_question_id):
    # if request.method == 'GET':
    #     data = request.POST
    #     video_path = data.get('video_path')
    #     # audio_path = data.get('audio_path')
    #     question_id = data.get('question_id')
    #     zoho_lead_id = data.get('zoho_lead_id')
    #     last_question_id=data.get('last_question_id')
    #     print("data",data)
        student_questions = {}  # Dictionary to store last question per student
        # print("testdsfsd")
        # try:
        #     # question_id = base64.b64decode(question_id).decode("utf-8")
        #     # zoho_lead_id = base64.b64decode(zoho_lead_id).decode("utf-8")
        #     # last_question_id = base64.b64decode(last_question_id).decode("utf-8")

        #     # print(question_id)
        #     # print(video_path)

        # except Exception as e:
        #     return JsonResponse({"error": f"Failed to decode Base64: {str(e)}"}, status=400)
        # Extract audio
        extracted_audio = extract_audio(video_path)
        if not extracted_audio:
            return JsonResponse({"error": "Audio extraction failed"}, status=500)

        try:
            transcribed_text = transcribe_audio(extracted_audio)
            sentiment_analysis = analyze_sentiment(transcribed_text)
            grammar_results = check_grammar(transcribed_text)

            # print(grammar_results)
            # print(sentiment_analysis)
            # subjectivity = sentiment_analysis["subjectivity"]
            # print(subjectivity)
            # print(zoho_lead_id)
            # print(question_id)
            # print(transcribed_text)
            # print(sentiment_analysis['sentiment_score'])
            # print(sentiment_analysis['subjectivity'])
            # print(sentiment_analysis['confidence_level'])
            # print(grammar_results['grammar_accuracy'])
            # print(last_question_id)

            try:
                check_answer_add = student_interview_answers(
                    zoho_lead_id,
                    question_id,
                    transcribed_text,
                    sentiment_analysis['sentiment_score'],
                    sentiment_analysis['subjectivity'],
                    sentiment_analysis['confidence_level'],
                    grammar_results['grammar_accuracy'],
                    last_question_id
                )
                print("Function executed successfully:", check_answer_add)
            except Exception as e:
                print("Error in function:", str(e))

            # async_task(check_answers("5204268000112707003"))
            print(r"test sdfdsfs:",last_question_id)
            print(r"test sdfdsfs asd:",zoho_lead_id)
            print(r"test sdfdsfs asd:",question_id)

           
            if int(last_question_id) == int(question_id):
                async_task(merge_videos(zoho_lead_id))
                async_task(check_answers(zoho_lead_id))
                # async_task("studentpanel.views.interview_process.merge_videos",zoho_lead_id)
                # async_task("studentpanel.views.interview_analyze.check_answers",zoho_lead_id)
                # print(async_task(check_answers("5204268000112707003")))
                # # async_task("studentpanel.views.interview_analyze.check_answers", zoho_lead_id)
                # # async_task("studentpanel.views.interview_analyze.merge_videos", "")
                # async_task("studentpanel.views.interview_analyze.check_answers", zoho_lead_id, sync=True)
            else:

                print("not asynk")


                    #
            return JsonResponse({
                "transcription": transcribed_text,
                "sentiment": sentiment_analysis,
                "grammar_results": grammar_results,
                "status": "success",
                "question_id": question_id,
                "zoho_lead_id": zoho_lead_id,
                # "confidence_level": confidence_level,
            })
            
        except Exception as e:
            return JsonResponse({"error": "Processing failed", "details": str(e)}, status=500)

    # return JsonResponse({"error": "Invalid request"}, status=400)


# print(async_task(check_answers('5204268000112707003')))

