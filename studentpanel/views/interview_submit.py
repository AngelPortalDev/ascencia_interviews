from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now
from studentpanel.models.student_interview_answer import StudentInterviewAnswers
from studentpanel.models.interview_link import StudentInterviewLink
# from studentpanel.models.student_Interview_status import StudentInterview

from django_q.tasks import async_task
import json
import base64

# @csrf_exempt
# def submit_interview(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             zoho_lead_id = data.get("zoho_lead_id")

#             if not zoho_lead_id:
#                 return JsonResponse({"error": "Missing zoho_lead_id"}, status=400)

#             print(f"Interview submitted at {now()} for {zoho_lead_id}")

#             async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)

#             return JsonResponse({"status": "merge triggered"}, status=200)

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     # ✅ Add this block for non-POST requests (like GET via browser)
#     return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

@csrf_exempt
def submit_interview(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            encoded_zoho_lead_id = data.get("zoho_lead_id")
            interview_link_count = data.get("interview_link_count")
            is_submitted = data.get("is_interview_submitted") is True

            if not encoded_zoho_lead_id:
                return JsonResponse({"error": "Missing zoho_lead_id"}, status=400)
            # ✅ Decode Base64 lead_id
            try:
                decoded_bytes = base64.b64decode(encoded_zoho_lead_id)
                zoho_lead_id = decoded_bytes.decode("utf-8")
            except Exception as decode_error:
                return JsonResponse({"error": "Invalid encoded zoho_lead_id"}, status=400)
            print("Decoded zoho_lead_id:", zoho_lead_id)
            if is_submitted:
                # Trigger async merge
                async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id,interview_link_count)
            return JsonResponse({"status": "merge triggered"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)
