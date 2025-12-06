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
from studentpanel.models.interview_link import StudentInterviewLink
from studentpanel.models.student_Interview_status import StudentInterview


from django.conf import settings
from django_q.tasks import async_task
from django.utils import timezone
from datetime import datetime
import pytz
import random
import json
from adminpanel.helper.email_branding import get_email_branding

from studentpanel.observer.tasks import save_interview_video, save_uploaded_chunk
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
# from studentpanel.tasks import merge_videos_task 
# from .serializers import QuestionSerializer
# from .serializers import QuestionSerializer
# @csrf_exempt
# def interview_attend(request):
#     if request.method == 'POST':
#         data = request.POST
#         zoho_lead_id_encoded = data.get('zoho_lead_id')

#         if not zoho_lead_id_encoded:
#             return JsonResponse({"error": "Student ID is required"}, status=400)

#         try:
#             # Decode the zoho_lead_id
#             zoho_lead_id = base64.b64decode(zoho_lead_id_encoded).decode("utf-8")
#             print(zoho_lead_id)
#             # Fetch student interview record
#             student_data = StudentInterviewLink.objects.get(zoho_lead_id=zoho_lead_id)
#             data = {
#                 'is_expired': student_data.is_expired,
#                 'expires_at'
#                 : student_data.expires_at
#             }
#             datetime_str = '2025-03-06 11:23:06.930063+05:30'

#             # Convert string to aware datetime object
#             expires_at = datetime.fromisoformat(datetime_str)

#             # Ensure expires_at is aware
#             if timezone.is_naive(expires_at):
#                 expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())

#             # Get current aware datetime
#             current_time = timezone.now()

#             # Check if the interview link has expired
#             if expires_at <= current_time:
#                 return JsonResponse({
#                     "status": True,
#                     "message": "Interview link has expired.",
#                     "expired_date": expired_date
#                 }, status=200)  # 410 GONE
#             else:
#                 is_expired = data['is_expired']
#                 # Check if interview link is expired
#                 if is_expired is True:
#                     print("test")
#                     expired_date = data['expires_at']
#                     return JsonResponse({
#                         "status": True,
#                         "message": "Interview link has expired.",
#                     }, status=200)  # 410 GONE
#                 else: 
#                     data = {
#                         'interview_attend': "true", 
#                         'is_expired': "true"
#                     }
#                     result = save_data(StudentInterviewLink, data, where={'zoho_lead_id': zoho_lead_id})
#                     if result['status']:
#                         return JsonResponse({"status": data, "message": "Interview attendance updated successfully"}, status=200)
#                     else:
#                         return JsonResponse({"status": data, "message": "Failed to update interview attendance"}, status=500)

#         except Exception as e:
#             return JsonResponse({"status": False, "message": "An error occurred while processing the request."}, status=500)

#     return JsonResponse({"status": False, "error": "Invalid request method"}, status=405)

# add for profile photo capture
@csrf_exempt
def upload_profile_photo(request):
    if request.method == 'POST' and 'image' in request.FILES:
        image_file = request.FILES['image']
        encoded_zoho_lead_id = request.POST.get('zoho_lead_id')

        try:
            zoho_lead_id = base64.b64decode(encoded_zoho_lead_id).decode("utf-8")
          
            
            profile_dir = os.path.join('static', 'uploads', 'profile_photos', zoho_lead_id)
            os.makedirs(profile_dir, exist_ok=True)

            # Save file
            profile_path = os.path.join(profile_dir, 'profile.jpg')
        

            with open(profile_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Relative path for DB
            relative_path = os.path.join('uploads', 'profile_photos', zoho_lead_id, 'profile.jpg')
            

            # Update Student_Interview model
            updated = StudentInterview.objects.filter(zoho_lead_id=zoho_lead_id).update(profile_photo=relative_path)

            if updated:
                return JsonResponse({
                    'message': 'Profile photo uploaded successfully',
                    'path': relative_path
                }, status=200)
            else:
                return JsonResponse({'error': 'Student_Interview record not found for this Zoho Lead ID.'}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Failed to decode zoho_lead_id: {str(e)}"}, status=500)

        # Create directory path
    return JsonResponse({'error': 'Image file is missing or request method is not POST'}, status=400)

@csrf_exempt
def interview_attend(request):
    if request.method == 'POST':
        data = request.POST
        zoho_lead_id_encoded = data.get('zoho_lead_id')
        encoded_interview_link_send_count= data.get('encoded_interview_link_send_count')
        print("encoded_interview_link_send_count",encoded_interview_link_send_count)
        if not zoho_lead_id_encoded:
            return JsonResponse({"error": "Student ID is required"}, status=400)

        try:
            # Decode the zoho_lead_id
            zoho_lead_id = base64.b64decode(zoho_lead_id_encoded).decode("utf-8")
            # print(zoho_lead_id)
            
            student_data_list = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id)

            for student_data in student_data_list:
                if encoded_interview_link_send_count == student_data.interview_link_count:

                    expires_at = student_data.expires_at
                    if timezone.is_naive(expires_at):
                        expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())

                    # Get current aware datetime
                    current_time = timezone.now()

            # Check if the interview link has expired
                    if expires_at <= current_time:
                        return JsonResponse({
                            "status": True, 
                            "message": "Interview link has expired.",
                            "expired_date": expires_at.strftime('%Y-%m-%d %H:%M:%S %Z')
                        }, status=410)
                    else:
                        # Update interview attendance and expiration status
                        interview_attend = student_data.interview_attend
                        # Check if interview link is expired
                        if interview_attend == 1:
                            expired_date = student_data.interview_attend
                            return JsonResponse({   
                                "status": True,
                                "message": "Interview link has expired.",
                            }, status=410) 
                             # 410 GONE
                        else:
                            # data = {
                            #   'interview_attend': True,  # Boolean value (not string)
                            #   'is_expired': True        # Boolean value (not string)
                            # } 

                            # result = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id).update(**data)
                            # if result == 1:
                            #     return JsonResponse({"status": data, "message": "Interview attendance updated successfully"}, status=200)
                            # else:
                            return JsonResponse({"status": "success", "message": "Interview attendance updated successfully"}, status=200)

        except StudentInterviewLink.DoesNotExist:
            return JsonResponse({"status": False, "message": "Student interview record not found."}, status=404)
        except base64.binascii.Error:
            return JsonResponse({"status": False, "message": "Invalid base64 encoding for zoho_lead_id."}, status=400)
        except Exception as e:
            return JsonResponse({"status": False, "message": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"status": False, "error": "Invalid request method"}, status=405)
# def interview_panel(request):
#     return render(request, "interview-panel.html") 


# def interview_score(request):
#     return render(request, "interview-score.html")


# def handle_uploaded_file(file,zoho_lead_id):

#     # upload_dir = os.path.join(settings.STUDENT_UPLOAD, 'uploads', 'interview_videos', zoho_lead_id)
#     upload_dir = os.path.join('static', 'uploads', 'interview_videos', zoho_lead_id)
#     os.makedirs(upload_dir, exist_ok=True)
#     file_path = os.path.join(upload_dir, file.name)
#     with open(file_path, 'wb+') as destination:
#         for chunk in file.chunks():
#             destination.write(chunk)
#     return file_path
# # app = Flask(__name__)
# # @app.route('/interveiw-section/interview_video_upload',methods=['POST'])


# @csrf_exempt
# def interview_video_upload(request):
#     if request.method == 'POST' and 'file' in request.FILES:
#         file = request.FILES['file']
#         encoded_zoho_lead_id = request.POST.get('zoho_lead_id')

#         try:
#             zoho_lead_id = base64.b64decode(encoded_zoho_lead_id).decode("utf-8")
#         except Exception as e:
#             return JsonResponse({"error": f"Failed to decode Base64: {str(e)}"}, status=400)

#         file_path = handle_uploaded_file(file, zoho_lead_id)

#         browser_name = request.POST.get("Browser Name")
#         browser_version = request.POST.get("Browser Version")
#         browser_info = f"{browser_name} {browser_version}" if browser_name and browser_version else None
        

#         try:
#             interview_link = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-id').first()
#             if interview_link:
#                 interview_link.browser_info = browser_info
#                 interview_link.save(update_fields=["browser_info"])
#         except Exception as e:
#             return JsonResponse({"error": f"Failed to save browser info: {str(e)}"}, status=500)

#         log_dir = os.path.join('static', 'uploads', 'profile_photos', zoho_lead_id)
#         os.makedirs(log_dir, exist_ok=True)
#         log_file_path = os.path.join(log_dir, "browser_info.txt")

#         if not os.path.exists(log_file_path):  # only create once
#             with open(log_file_path, "w", encoding="utf-8") as f:
#                 f.write("===== Browser Info =====\n")
#                 f.write(f"Browser Name: {browser_name}\n")
#                 f.write(f"Browser Version: {browser_version}\n")
#                 f.write(f"Captured At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
#                 f.write("========================\n")

#         return JsonResponse({
#             'message': 'File successfully uploaded',
#             'file_path': file_path,
#             'browser_log': log_file_path if os.path.exists(log_file_path) else None
#         })
#         # async_task(studentpanel.views.interview_process.analyze_video(video_path,audio_path,))

#         return JsonResponse({'message': 'File successfully uploaded', 'file_path': file_path})
    
#     return JsonResponse({'error': 'No file part in the request'}, status=400)


# studentpanel/views.py


@csrf_exempt
def interview_video_upload(request):
    """
    Unified API to handle:
    1️⃣ Single video file upload
    2️⃣ Chunked upload for large videos
    All uploads are sent to Celery asynchronously.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

    # ---- Single video upload ----
    if 'file' in request.FILES:
        file = request.FILES['file']
        encoded_zoho_lead_id = request.POST.get('zoho_lead_id')

        try:
            zoho_lead_id = base64.b64decode(encoded_zoho_lead_id).decode("utf-8")
        except Exception as e:
            return JsonResponse({"error": f"Failed to decode Base64: {str(e)}"}, status=400)

        file_bytes = file.read()
        file_name = file.name
        browser_name = request.POST.get("Browser Name")
        browser_version = request.POST.get("Browser Version")

        # Build return path for interview_add_video_path()
        # video_path = f"uploads/interview_videos/{zoho_lead_id}/{file_name}"
        video_path = f"static/uploads/interview_videos/{zoho_lead_id}/{file_name}"


        # Send to Celery
        async_result = save_interview_video.delay(
            file_bytes,
            file_name,
            zoho_lead_id,
            browser_name,
            browser_version
        )

        return JsonResponse({
            "status": "success",
            "message": "Full video upload triggered, processing in background",
            "celery_task_id": async_result.id,
            "file_path": video_path  # <-- Added so React can call interview_add_video_path()
            # 'file_path': file_path,
        })

    # ---- Chunked video upload ----
    elif 'chunk' in request.FILES:
        question_id = request.POST.get('questionId')
        chunk_index = request.POST.get('chunkIndex')
        chunk_file = request.FILES.get('chunk')

        if not all([question_id, chunk_index, chunk_file]):
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)

        file_bytes = chunk_file.read()
        file_name = chunk_file.name

        # Send chunk to Celery
        async_result = save_uploaded_chunk.delay(file_bytes, file_name, question_id, chunk_index)

        return JsonResponse({
            "status": "success",
            "message": "Chunk upload triggered",
            "chunkIndex": chunk_index,
            "celery_task_id": async_result.id
        })

    else:
        return JsonResponse({'error': 'No file or chunk part in the request'}, status=400)


# @csrf_exempt
# def interview_video_upload(request):
#     if request.method == 'POST' and 'file' in request.FILES:
#         file = request.FILES['file']
#         encoded_zoho_lead_id = request.POST.get('zoho_lead_id')

#         try:
#             zoho_lead_id = base64.b64decode(encoded_zoho_lead_id).decode("utf-8")
#         except Exception as e:
#             return JsonResponse({"error": f"Failed to decode Base64: {str(e)}"}, status=400)

#         file_path = handle_uploaded_file(file, zoho_lead_id)

#         # Count videos in directory
#         folder_path = os.path.join(settings.STUDENT_UPLOAD, 'uploads', 'interview_videos', zoho_lead_id)
#         video_count = len([f for f in os.listdir(folder_path) if f.endswith('.mp4')])
#         print(video_count)

#         # Trigger merge only when 5 videos are uploaded
#         if video_count == 5:
#             print("Triggering Celery task")
#             merge_videos_task.delay(zoho_lead_id)

#         return JsonResponse({'message': 'File successfully uploaded', 'file_path': file_path})
    
#     return JsonResponse({'error': 'No file part in the request'}, status=400)



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



# @csrf_exempt
# def interview_questions(request):
#     try:
#         questions = CommonQuestion.objects.all()
#         question_data = [
#             {
#                 'question': question.question,
#                 # 'answer': question.answer,
#                 'encoded_id': question.id
#             }
#             for question in questions
#         ]
#         return JsonResponse({'questions': question_data}, status=200)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


def assign_questions_to_interview_link(interview_link, crm_id, count=6):
    if interview_link.assigned_question_ids:
        return  # Already assigned

    all_questions = list(CommonQuestion.objects.filter(crm_id=crm_id).order_by('id'))
    if len(all_questions) < count:
        raise ValueError("Not enough questions available")

    # Always pick first 3
    first_three = all_questions[:3]

    # Randomly pick 3 more from remaining
    remaining = all_questions[3:]
    if len(remaining) < 3:
        raise ValueError("Not enough remaining questions for random selection")

    import random
    random_three = random.sample(remaining, 3)

    final_questions = first_three + random_three
    selected_ids = [str(q.id) for q in final_questions]

    interview_link.assigned_question_ids = ",".join(selected_ids)
    interview_link.save()

@csrf_exempt
def interview_questions(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    encoded_id = data.get('zoho_lead_id')
    interview_link_count = data.get('interview_link_count')
    if not encoded_id or not interview_link_count:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        zoho_lead_id = base64.b64decode(encoded_id).decode('utf-8')
    except Exception as e:
        return JsonResponse({'error': f'Invalid encoding: {str(e)}'}, status=400)

    try:
        interview_link = StudentInterviewLink.objects.get(
            zoho_lead_id=zoho_lead_id,
            interview_link_count=interview_link_count
        )
    except StudentInterviewLink.DoesNotExist:
        return JsonResponse({'error': 'Interview link not found'}, status=404)

    # Get Student & Institute
    try:
        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        institute = Institute.objects.get(crm_id=student.crm_id)
    except (Students.DoesNotExist, Institute.DoesNotExist):
        return JsonResponse({'error': 'Student or Institute not found'}, status=404)

    # Fetch questions
    common_questions = list(CommonQuestion.active_objects.filter(crm_id=institute))
    course_questions = []
    if student.program:
        matched_course = Course.active_objects.filter(
            course_name__iexact=student.program.strip(),
            crm_id=institute
        ).first()
        if matched_course:
            course_questions = list(Question.active_objects.filter(course_id=matched_course))

    # ----------------------------
    # ✅ Assign questions logic
    # ----------------------------
    # ----- Assign Common Questions -----
    if not interview_link.assigned_question_ids:
        print("🟡 Assigning COMMON questions...")

        if str(institute.crm_id) in ["755071407", "759439531"]:
            selected_common = common_questions
        else:
            # first_three = common_questions[:3]
            # remaining_common = common_questions[3:]
            # random_three = random.sample(
            #     remaining_common, 
            #     min(3, len(remaining_common))
            # ) if remaining_common else []
            # selected_common = first_three + random_three
            selected_common = common_questions
            print("Selected COMMON Questions IDs:", [q.id for q in selected_common])

        interview_link.assigned_question_ids = ",".join(str(q.id) for q in selected_common)
        print("🟢 Saved COMMON:", interview_link.assigned_question_ids)

    # ----- Assign Course Questions -----
    if not interview_link.assigned_course_question_ids:
        print("🟡 Assigning COURSE questions...")

        selected_course = course_questions if course_questions else []
        interview_link.assigned_course_question_ids = ",".join(str(q.id) for q in selected_course)

        print("🟢 Saved COURSE:", interview_link.assigned_course_question_ids)

    interview_link.save()
    # ----------------------------
    # ✅ Prepare response
    # ----------------------------
    common_ids = list(map(int, interview_link.assigned_question_ids.split(','))) if interview_link.assigned_question_ids else []
    course_ids = list(map(int, interview_link.assigned_course_question_ids.split(','))) if interview_link.assigned_course_question_ids else []

    # Fetch questions
    common_qs = {q.id: q for q in CommonQuestion.objects.filter(id__in=common_ids)}
    course_qs = {q.id: q for q in Question.objects.filter(id__in=course_ids)}

    ordered_data = []

    # Common questions first
    for qid in common_ids:
        q_obj = common_qs.get(qid)
        if q_obj:
            ordered_data.append({
                'encoded_id': qid,
                'question': q_obj.question,
                'time_limit': getattr(q_obj, 'time_limit', 30)
            })

    # Course questions next
    for qid in course_ids:
        q_obj = course_qs.get(qid)
        if q_obj:
            ordered_data.append({
                'encoded_id': qid,
                'question': q_obj.question,
                'time_limit': getattr(q_obj, 'time_limit', 30)
            })

    return JsonResponse({'questions': ordered_data}, status=200)

    
@csrf_exempt
def student_data(request):
    if request.method == 'POST':
        data = request.POST
        zoho_lead_id = data.get('zoho_lead_id')
        if not zoho_lead_id:
            return JsonResponse({"error": "student id does not exists"}, status=500)
        try:
            decoded_bytes = base64.b64decode(zoho_lead_id)
            zoho_lead_id = decoded_bytes.decode("utf-8")  # Convert bytes to string
            student = Students.objects.get(zoho_lead_id=zoho_lead_id)
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
    
    return JsonResponse({'error': 'No file part in the request'}, status=400)


@csrf_exempt
def get_branding_by_zoho_id(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        data = json.loads(request.body)
        encoded_zoho_lead_id = data.get("zoho_lead_id")
        if not encoded_zoho_lead_id:
            return JsonResponse({"error": "Missing zoho_lead_id"}, status=400)

        zoho_lead_id = base64.b64decode(encoded_zoho_lead_id).decode("utf-8")
        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        crm_id = student.crm_id

        logo_url, company_name = get_email_branding(str(crm_id))
        print("logo_url and company name",logo_url, company_name)
        return JsonResponse({"success": True, "logo_url": logo_url, "company_name": company_name})
    except Students.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)