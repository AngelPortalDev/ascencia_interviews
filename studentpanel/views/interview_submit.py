from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now
from studentpanel.models.student_interview_answer import StudentInterviewAnswers
from studentpanel.models.interview_link import StudentInterviewLink
from studentpanel.models.student_Interview_status import Student_Interview

from django_q.tasks import async_task
import json

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
            # Parse raw JSON body
            data = json.loads(request.body)
            zoho_lead_id = data.get("zoho_lead_id")
            print("zoho_lead_id",zoho_lead_id)
            interview_link_count = data.get("interview_link_count")
            is_submitted = data.get("is_interview_submitted") is True

            if not zoho_lead_id:
                return JsonResponse({"error": "Missing zoho_lead_id"}, status=400)

            print(f"Interview submitted at {now()} for {zoho_lead_id}")

            if is_submitted:
                # student = Student_Interview.objects.get(zoho_lead_id=zoho_lead_id)
                # student.is_interview_submitted = True
                # student.save()
                async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)

                  # update interview attend complete interview that time link expire
                update_result = StudentInterviewLink.objects.filter(
                            zoho_lead_id=zoho_lead_id,
                            interview_link_count=interview_link_count
                        ).update(interview_attend=True, is_expired=True)

            return JsonResponse({"status": "merge triggered"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)