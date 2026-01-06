import requests
import uuid
import time
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import AllowAny
from django_q.tasks import async_task
import os

from sklearn import base
from studentpanel.models.interview_process_model import Students
from studentpanel.models.interview_link import StudentInterviewLink
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from api.tasks import get_assigned_questions_count,get_recorded_questions_count


import logging

logger = logging.getLogger('zoho_webhook_logger')

DAILY_API_URL = "https://api.daily.co/v1"
DAILY_API_KEY = "6bde2a9e8a80082522e59abebd2769ef7f6b1c88ca2f842ce99a7968a71f87a3"

# ============ DAILY.CO TOKEN ENDPOINT ============
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def get_daily_token(request):

#     try:
#         print("📍 [get_daily_token] Request received")
        
#         # Parse request body (optional)
#         try:
#             body = json.loads(request.body.decode("utf-8"))
#         except Exception:
#             body = {}

#         # ✅ Step 1: Create unique room
#         room_name = f"interview-{uuid.uuid4()}"
#         print(f"🔹 Creating room: {room_name}")

#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {DAILY_API_KEY}",
#         }

#         room_payload = {
#             "name": room_name,
#             "properties": {
#                 "enable_recording": "cloud",
#                 "max_participants": 2, 
#                 "exp": int(time.time()) + 3600,
#                 "enable_chat": False,
#                 "enable_screenshare": False,
#             },
#         }

#         # Create room on Daily.co
#         room_res = requests.post(
#             f"{DAILY_API_URL}/rooms",
#             headers=headers,
#             json=room_payload,
#         )

#         print(f"🔹 Room creation response: {room_res.status_code}")
        
#         if room_res.status_code not in [200, 201]:
#             error_msg = f"Room creation failed: {room_res.text}"
#             print(f"❌ {error_msg}")
#             return JsonResponse(
#                 {"error": "Room creation failed", "details": room_res.text},
#                 status=500,
#             )

#         room_data = room_res.json()
#         room_url = room_data.get("url")
#         print(f"✅ Room created: {room_url}")

#         # ✅ Step 2: Create meeting token
#         token_payload = {
#             "properties": {
#                 "room_name": room_name,
#                 "is_owner": True,
#                 # "start_cloud_recording": True, 
#                 "exp": int(time.time()) + 3600,
#             }
#         }

#         token_res = requests.post(
#             f"{DAILY_API_URL}/meeting-tokens",
#             headers=headers,
#             json=token_payload,
#         )

#         print(f"🔹 Token creation response: {token_res.status_code}")

#         if token_res.status_code != 200:
#             error_msg = f"Token creation failed: {token_res.text}"
#             print(f"❌ {error_msg}")
#             return JsonResponse(
#                 {"error": "Token creation failed", "details": token_res.text},
#                 status=500,
#             )

#         token_data = token_res.json()
#         token = token_data.get("token")
#         print(f"✅ Token created successfully")
        
#         update_payload = {
#             "width": 1280,
#             "height": 720,
#             # "videoBitrate": 3000,  # kbps
#             # "audioBitrate": 96
#         }
        
#         update_res = requests.post(
#             f"{DAILY_API_URL}/rooms/{room_name}/recordings/update",
#             headers=headers,
#             json=update_payload,
#         )

#         if update_res.status_code not in [200, 201]:
#             print(f"⚠️ Recording update failed: {update_res.text}")

#         # ✅ Step 3: Return response
#         response_data = {
#             "room_name": room_name,
#             "room_url": room_url,
#             "token": token,
#         }
        
#         print(f"✅ [get_daily_token] Success: {response_data}")
#         return JsonResponse(response_data, status=200)

#     except Exception as e:
#         error_msg = f"Exception: {str(e)}"
#         print(f"❌ [get_daily_token] {error_msg}")
#         return JsonResponse({"error": error_msg}, status=500)

@csrf_exempt
@api_view(["POST"])
@authentication_classes([])   
@permission_classes([AllowAny])
def get_daily_token(request):
    try:
        zoho_lead_id = request.data.get("zoho_lead_id")

        
        if not zoho_lead_id:
            return JsonResponse(
                {"error": "zoho_lead_id is required"},
                status=400
            )

        print("📍 [get_daily_token] zoho_lead_id:", zoho_lead_id)

        # Step 1: Create unique room
        room_name = f"interview-{zoho_lead_id}"
        print(f"🔹 Creating room: {room_name}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DAILY_API_KEY}",
        }

        room_payload = {
            "name": room_name,
            "properties": {
                "enable_recording": "cloud",
                "max_participants": 2,
                "exp": int(time.time()) + 3600,
                "enable_chat": False,
                "enable_screenshare": False,
            },
        }

        try:
            room_res = requests.post(f"{DAILY_API_URL}/rooms", headers=headers, json=room_payload, timeout=15)
        except Exception as e:
            print(f"❌ [get_daily_token] Room creation request failed: {e}")
            return JsonResponse({"error": "room_creation_request_failed", "details": str(e)}, status=502)

        # Handle room creation response; if the room already exists, fetch it
        if room_res.status_code in [200, 201]:
            room_data = room_res.json()
            room_url = room_data.get("url")
            print(f"✅ Room created: {room_url}")
        else:
            # Log details for debugging
            try:
                body = room_res.text
            except Exception:
                body = "<no-body>"

            # Daily.co returns 400 when a room with the same name already exists
            if room_res.status_code == 400 and ("already exists" in body or "already_exists" in body):
                print(f"⚠️ [get_daily_token] Room already exists, fetching existing room: {room_name}")
                try:
                    get_res = requests.get(f"{DAILY_API_URL}/rooms/{room_name}", headers=headers, timeout=10)
                except Exception as e:
                    print(f"❌ [get_daily_token] Failed to fetch existing room: {e}")
                    return JsonResponse({"error": "fetch_existing_room_failed", "details": str(e)}, status=502)

                if get_res.status_code in [200, 201]:
                    try:
                        room_data = get_res.json()
                        room_url = room_data.get("url")
                        print(f"✅ Fetched existing room: {room_url}")
                    except Exception as e:
                        print(f"❌ [get_daily_token] Failed to parse existing room response: {e}")
                        return JsonResponse({"error": "parse_existing_room_failed", "details": str(e)}, status=502)
                else:
                    print(f"❌ [get_daily_token] Fetch existing room returned status {get_res.status_code}: {get_res.text}")
                    return JsonResponse({"error": "fetch_existing_room_failed", "details": get_res.text}, status=502)
            else:
                print(f"❌ [get_daily_token] Room creation returned status {room_res.status_code}: {body}")
                return JsonResponse({"error": "Room creation failed", "details": body}, status=502)

        # Step 2: Create meeting token
        token_payload = {
            "properties": {
                "room_name": room_name,
                "is_owner": True,
                "exp": int(time.time()) + 3600,
            }
        }

        try:
            token_res = requests.post(f"{DAILY_API_URL}/meeting-tokens", headers=headers, json=token_payload, timeout=15)
        except Exception as e:
            print(f"❌ [get_daily_token] Token request failed: {e}")
            return JsonResponse({"error": "token_request_failed", "details": str(e)}, status=502)

        if token_res.status_code != 200:
            try:
                t_body = token_res.text
            except Exception:
                t_body = "<no-body>"
            print(f"❌ [get_daily_token] Token creation returned status {token_res.status_code}: {t_body}")
            return JsonResponse({"error": "Token creation failed", "details": t_body}, status=502)

        token_data = token_res.json()
        token = token_data.get("token")
        print(f"✅ Token created successfully")

        # Return response
        return JsonResponse(
            {
                "room_name": room_name,
                "room_url": room_data.get("url"),
                "token": token_res.json().get("token"),
                "zoho_lead_id": zoho_lead_id,  # optional echo
            },
            status=200
        )

    except Exception as e:
        print(f"❌ [get_daily_token] Exception: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

 
    
    
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def start_daily_recording(request):
#     try:
#         room_name = request.data.get("room_name")
#         if not room_name:
#             return JsonResponse({"error": "room_name missing"}, status=400)

#         headers = {
#             "Authorization": f"Bearer {DAILY_API_KEY}",
#             "Content-Type": "application/json",
#         }

#         print("Starting recording for:", room_name)

#         res = requests.post(
#             f"https://api.daily.co/v1/rooms/{room_name}/recordings/start",
#             headers=headers,   
#             json={},           # ✅ EMPTY PAYLOAD
#             timeout=10
#         )

#         print("Daily status:", res.status_code)
#         print("Daily body:", res.text)

#         if res.status_code not in (200, 201):
#             return JsonResponse(
#                 {"error": "Recording start failed", "details": res.text},
#                 status=res.status_code
#             )

#         return JsonResponse(res.json(), status=200)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def start_daily_recording(request):
    try:
        room_name = request.data.get("room_name")
        question_number = request.data.get("question_number")
        zoho_lead = request.data.get("zoho_lead_id") or request.data.get("zoho_lead")
        
        if not room_name:
            return JsonResponse({"error": "room_name is required"}, status=400)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DAILY_API_KEY}",
        }
        

        # 🚫 CRITICAL: Prevent overlapping recordings
        check = requests.get(
            f"{DAILY_API_URL}/rooms/{room_name}/recordings",
            headers=headers,
            timeout=10
        )

        if check.status_code == 200:
            active = [
                r for r in check.json().get("data", [])
                if r.get("status") == "recording"
            ]
            if active:
                return JsonResponse(
                    {"error": "Recording already running. Stop previous recording first."},
                    status=409
                )

        # Start recording for this room with proper layout object
        response = requests.post(
            f"{DAILY_API_URL}/rooms/{room_name}/recordings/start",
            headers=headers,
            json={
                "type": "cloud",
                "layout": {
                    "preset": "default"
                }
            }
        )
        
        print(f" Response Status: {response.status_code}")
        print(f" Full Response: {response.json()}")  # DEBUG: Print entire response
        
        if response.status_code not in [200, 201]:
            return JsonResponse(
                {"error": "Failed to start recording", "details": response.text},
                status=500
            )
        
        recording_data = response.json()
        print(f" Recording Data: {recording_data}")  # DEBUG
        
        # Try different keys that might contain the ID
        recording_id = (
            recording_data.get("id") or 
            recording_data.get("recordingId") or 
            recording_data.get("data", {}).get("id") or
            str(question_number)  # Fallback: use question number as ID
        )
        
        print(f" Recording started for Q{question_number}: {recording_id}")

        # Persist mapping of question_number -> recording_id in existing interview row (do NOT create new)
        try:
            if zoho_lead:
                interview_row = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead).order_by('-id').first()
            else:
                # try to parse zoho from room_name like 'interview-<zoho>-...'
                interview_row = None
                if room_name and room_name.startswith('interview-'):
                    parts = room_name.split('-')
                    if len(parts) >= 2:
                        candidate_zoho = parts[1]
                        interview_row = StudentInterviewLink.objects.filter(zoho_lead_id=candidate_zoho).order_by('-id').first()

            if interview_row:
                    # store started recording mapping in recording_json.started_recordings
                    # Merge/update semantics: avoid creating duplicate entries for the
                    # same question_number. If an entry for the question exists, update
                    # its recording_id; otherwise add it. This prevents repeated
                    # additions like seeing question 9 appended multiple times.
                    rjson = interview_row.recording_json or {}
                    existing_started = []
                    if isinstance(rjson, dict):
                        es = rjson.get('started_recordings')
                        if isinstance(es, list):
                            existing_started = [i for i in es if isinstance(i, dict)]

                    def key_of(item):
                        q = item.get('question_number')
                        if q is not None:
                            return str(q)
                        rid = item.get('recording_id') or item.get('recordingId')
                        return f"rid:{rid}" if rid else None

                    merged_map = {}
                    for it in existing_started:
                        k = key_of(it)
                        if k is not None:
                            merged_map[k] = it

                    # new/updated entry
                    new_item = {'question_number': question_number, 'recording_id': recording_id}
                    nk = key_of(new_item)
                    if nk is not None:
                        merged_map[nk] = new_item

                    # convert back to list ordered by numeric question_number when possible
                    def sort_key(it):
                        try:
                            return int(it.get('question_number'))
                        except Exception:
                            return float('inf')

                    merged_list = sorted(list(merged_map.values()), key=sort_key)
                    rjson['started_recordings'] = merged_list
                    interview_row.recording_json = rjson
                    interview_row.save(update_fields=['recording_json'])
        except Exception as e:
            print(f"Could not persist start-recording mapping: {e}")
        
        return JsonResponse({
            "recording_id": recording_id,
            "question_number": question_number,
            "status": "recording",
            "data": recording_data
        }, status=200)
        
    except Exception as e:
        print(f" Exception: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def stop_daily_recording(request):
    logger.info("[stop_daily_recording] CALLED")

    try:
        # Accept both DRF Request (request.data) and Django HttpRequest (request.body)
        if hasattr(request, 'data'):
            req_data = request.data
        else:
            try:
                req_data = json.loads(request.body.decode('utf-8')) if request.body else {}
                logger.info(
                "[stop_daily_recording] Payload received: %s",
                req_data
            )

            except Exception:
                req_data = {}

        # The user wants only to persist the JSON payload (e.g. {"started_recordings": [...]})
        print(f"[stop_daily_recording] Persisting recording JSON payload: {req_data}")

        # Extract fields
        zoho_lead = req_data.get('zoho_lead_id') or req_data.get('zoho_lead') or None
        room_name = req_data.get('room_name') or req_data.get('room')
        recording_id = req_data.get('recording_id') or req_data.get('recordingId')

        logger.info(
        "[stop_daily_recording] Extracted zoho=%s room=%s rid=%s",
        zoho_lead, room_name, recording_id
    )


        # Attempt to stop the recording on Daily.co so the room becomes idle for the next start
        try:
            headers_daily = {'Authorization': f'Bearer {DAILY_API_KEY}', 'Content-Type': 'application/json'}
            stop_ok = False
            stop_responses = []
            # First try stopping by recording id (preferred)
            # ✅ STOP DAILY RECORDING — ROOM ONLY (CORRECT)
            try:
                if not room_name:
                    raise ValueError("room_name is required to stop recording")

                stop_url = f"{DAILY_API_URL}/rooms/{room_name}/recordings/stop"

                print(f"[stop_daily_recording] Stopping Daily recording via ROOM: {room_name}")
                logger.info(
                    "[stop_daily_recording] Daily STOP via room zoho=%s room=%s",
                    zoho_lead, room_name
                )

                r = requests.post(
                    stop_url,
                    headers=headers_daily,
                    json={},
                    timeout=10
                )

                stop_responses.append((stop_url, r.status_code, r.text))

                if r.status_code in (200, 201):
                    stop_ok = True
                else:
                    stop_ok = False

            except Exception as e:
                stop_ok = False
                stop_responses.append(("room_stop_exception", None, str(e)))

            # Fallback: stop by room endpoint
            if not stop_ok and room_name:
                try:
                    stop_url = f"{DAILY_API_URL}/rooms/{room_name}/recordings/stop"
                    # stop_url = f"{DAILY_API_URL}/rooms/{room_name}/recordings/stop"
                    print(f"[stop_daily_recording] Attempting stop via room name: {room_name}")
                    logger.info(
                    "[stop_daily_recording] Attempting Daily STOP zoho=%s room=%s rid=%s",
                    zoho_lead, room_name, recording_id
                )

                    r2 = requests.post(stop_url, headers=headers_daily, json={}, timeout=10)
                    stop_responses.append((stop_url, r2.status_code, r2.text))
                    if r2.status_code in (200, 201):
                        stop_ok = True
                except Exception as e:
                    stop_responses.append((f"room_stop_exception:{room_name}", None, str(e)))

            print(f"[stop_daily_recording] stop attempts: {stop_responses}")

            logger.info(
            "[stop_daily_recording] Stop responses ok=%s responses=%s",
            stop_ok, stop_responses
        )


            # If we issued a stop, poll the recording metadata briefly to ensure the recording is no longer 'recording'
            
        except Exception as e:
            print(f"[stop_daily_recording] error while attempting stop: {e}")
        if not zoho_lead and room_name and isinstance(room_name, str) and room_name.startswith('interview-'):
            parts = room_name.split('-')
            if len(parts) >= 2:
                zoho_lead = parts[1]

        if not zoho_lead:
            # Do not attempt downloads; require zoho_lead for persistence
            return JsonResponse({"ok": False, "message": "zoho_lead_id required to persist recording JSON"}, status=400)

        # Find existing interview link row for this zoho_lead (do NOT create a new one)
        interview_row = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead).order_by('-id').first()
        logger.info(
        "[stop_daily_recording] Interview row found=%s zoho=%s",
        bool(interview_row), zoho_lead
    )

        if not interview_row:
            return JsonResponse({"ok": False, "message": "No existing StudentInterviewLink for zoho_lead", "zoho_lead": zoho_lead}, status=200)

        # Persist the incoming JSON into the model's recording_json field
        # Merge semantics: keep any previously stored started_recordings and
        # merge/update entries from the incoming payload so we don't lose
        # recordings collected earlier in the session.
        try:
            existing = interview_row.recording_json or {}
            merged = {} if not isinstance(existing, dict) else dict(existing)

            # Pull incoming started_recordings (if any). If the payload does
            # not include a list but has a single recording_id+question_number,
            # normalise it into a list.
            incoming_started = []
            if isinstance(req_data, dict):
                inc = req_data.get('started_recordings')
                if isinstance(inc, list):
                    incoming_started = [i for i in inc if isinstance(i, dict)]
                else:
                    # fallback: single pair in top-level keys
                    rid = req_data.get('recording_id') or req_data.get('recordingId')
                    qn = req_data.get('question_number') or req_data.get('question')
                    if rid and qn is not None:
                        incoming_started = [{'question_number': qn, 'recording_id': rid}]

            # Existing started list
            existing_started = []
            if isinstance(existing, dict):
                es = existing.get('started_recordings')
                if isinstance(es, list):
                    existing_started = [i for i in es if isinstance(i, dict)]

            # Build a map keyed by question_number (stringified) so incoming
            # entries overwrite/update existing ones for the same question.
            merged_map = {}
            def key_of(item):
                k = item.get('question_number')
                return str(k) if k is not None else None

            for it in existing_started:
                k = key_of(it)
                if k is not None:
                    merged_map[k] = it

            for it in incoming_started:
                k = key_of(it)
                if k is not None:
                    merged_map[k] = it

            # Convert map back to sorted list (by numeric question_number when possible)
            def sort_key(it):
                try:
                    return int(it.get('question_number'))
                except Exception:
                    return float('inf')

            merged_started = sorted(list(merged_map.values()), key=sort_key)

            # Merge other top-level keys from incoming payload into merged dict,
            # but let started_recordings be the merged list we just built.
            if isinstance(req_data, dict):
                for k, v in req_data.items():
                    if k == 'started_recordings':
                        continue
                    merged[k] = v

            merged['started_recordings'] = merged_started

            interview_row.recording_json = merged
            interview_row.process_status = 'recordings_saved'
            interview_row.save(update_fields=['recording_json', 'process_status'])

            logger.info(
            "[stop_daily_recording] recording_json saved interview_id=%s status=%s",
            interview_row.id,
            interview_row.process_status
        )



            # ---------------------------------------------------
            # ✅ CHECK INTERVIEW COMPLETE → TRIGGER DOWNLOAD (DEBUG)
            # ---------------------------------------------------
            try:
                print("🧪 INTERVIEW COMPLETE CHECK STARTED")

                print(f"🧾 Interview ID: {interview_row.id}")
                print(f"🧾 Zoho Lead: {interview_row.zoho_lead_id}")
                print(f"🧾 Current process_status: {interview_row.process_status}")

                assigned_count = get_assigned_questions_count(interview_row)
                recorded_count = get_recorded_questions_count(interview_row)
                logger.info(
                "[stop_daily_recording] Completion check interview_id=%s assigned=%s recorded=%s",
                interview_row.id, assigned_count, recorded_count
            )


                print(f"📊 Assigned questions count : {assigned_count}")
                print(f"📊 Recorded questions count : {recorded_count}")

                print(f"🗂 assigned_question_ids: {interview_row.assigned_question_ids}")
                print(f"🗂 assigned_course_question_ids: {interview_row.assigned_course_question_ids}")

                print(f"🎥 recording_json raw: {interview_row.recording_json}")

                if assigned_count <= 0:
                    print("⚠️ No assigned questions found")

                if assigned_count == recorded_count:
                    print("✅ Assigned == Recorded")

                    if interview_row.process_status == "download_triggered":
                        print("⛔ Download already triggered earlier — skipping")
                    else:
                        print("🚀 Triggering Daily download task...")

                        from django_q.tasks import async_task
                        from django.conf import settings

                        daily_api_key = getattr(settings, 'DAILY_API_KEY', None)

                        print(f"🔐 DAILY_API_KEY present: {bool(daily_api_key)}")
                        logger.info(
                        "[stop_daily_recording] Triggering download task interview_id=%s zoho=%s",
                        interview_row.id,
                        interview_row.zoho_lead_id,
                        daily_api_key
                    )
                        
                        task_id = async_task(
                            'api.tasks.download_recordings_job',
                            interview_row.zoho_lead_id,
                            None, None, None,
                            interview_row.id,
                            daily_api_key
                        )

                        logger.info(
                        "[stop_daily_recording] async_task QUEUED task_id=%s",
                        task_id
                    )

                        interview_row.process_status = "download_triggered"
                        interview_row.save(update_fields=["process_status"])
                        logger.info(
                        "[stop_daily_recording] Status updated → download_triggered interview_id=%s",
                        interview_row.id
                    )


                        print("🎯 DOWNLOAD TASK TRIGGERED SUCCESSFULLY")
                else:
                    print("⏳ Interview NOT complete yet — waiting for more recordings")
                    logger.info(
                    "[stop_daily_recording] Interview not complete interview_id=%s assigned=%s recorded=%s",
                    interview_row.id, assigned_count, recorded_count
                )


            except Exception as e:
                logger.exception("[stop_daily_recording] Unhandled exception")

                import traceback
                print("❌ INTERVIEW COMPLETE CHECK FAILED")
                traceback.print_exc()

            # Attempt to enqueue background download job so recordings are fetched
            # try:
            #     # async_task('api.tasks.download_recordings_job', zoho_lead, None, None, None, interview_row.id, getattr(settings, 'DAILY_API_KEY', None))
            #     # print(f"[stop_daily_recording] queued download_recordings_job for zoho_lead={zoho_lead} interview_id={interview_row.id}")
            # except Exception as e:
            #     print(f"[stop_daily_recording] failed to queue download job: {e}")
        except Exception as e:
            logger.exception("[stop_daily_recording] Unhandled exception")

            print(f"[stop_daily_recording] Failed to save recording JSON: {e}")
            return JsonResponse({"ok": False, "message": "save_failed", "error": str(e)}, status=500)

        return JsonResponse({"ok": True, "message": "recording_json_saved", "zoho_lead": zoho_lead}, status=200)
    except Exception as e:
        logger.exception("[stop_daily_recording] Unhandled exception")

        print(f"[stop_daily_recording] Exception: {e}")
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def download_recordings(request):
    """Download recordings for an interview (trigger after interview submit).

    Accepts POST JSON with one of:
      - {"interview_id": 123}
      - {"zoho_lead_id": "520..."}
      - {"recording_ids": ["id1","id2"], "zoho_lead_id": "..."}

    Behaviour:
      - If recording_ids provided, uses that list. Otherwise reads from
        StudentInterviewLink.recording_json.started_recordings (list of {question_number, recording_id}).
      - For each recording id, calls Daily.co recordings/{id}/access-link or recordings/{id}
        to obtain a download URL (looks for keys: download_link, download_url, url).
      - Downloads files immediately into `static/uploads/<zoho_lead>/raw/` and updates
        StudentInterviewLink.recording_files (list of dicts) and maps files to
        StudentInterviewAnswers.video_path when question mapping available.
    """
    try:
        # Parse input
        if hasattr(request, 'data'):
            payload = request.data
        else:
            try:
                payload = json.loads(request.body.decode('utf-8')) if request.body else {}
            except Exception:
                payload = {}

        interview_id = payload.get('interview_id')
        zoho_lead = payload.get('zoho_lead_id') or payload.get('zoho_lead')
        recording_ids = payload.get('recording_ids')

        # Resolve interview row
        interview_row = None
        if interview_id:
            interview_row = StudentInterviewLink.objects.filter(id=interview_id).first()
            zoho_lead = zoho_lead or (getattr(interview_row, 'zoho_lead_id', None) if interview_row else None)
        elif zoho_lead:
            interview_row = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead).order_by('-id').first()

        if not interview_row and not zoho_lead and not recording_ids:
            return JsonResponse({"ok": False, "message": "Provide interview_id or zoho_lead_id or recording_ids"}, status=400)

        zoho_lead = zoho_lead or (getattr(interview_row, 'zoho_lead_id', None) if interview_row else None)
        if not zoho_lead:
            return JsonResponse({"ok": False, "message": "zoho_lead_id required to store files"}, status=400)

        # Build the list of (question_number, recording_id) tuples
        recordings = []  # list of dicts: {'question_number': n or None, 'recording_id': id}
        # Support filtering: single question_id or list question_ids
        question_id = payload.get('question_id') or payload.get('question_number')
        question_ids = payload.get('question_ids')

        if recording_ids and isinstance(recording_ids, (list, tuple)):
            # If explicit list provided, optionally filter by question_ids (if provided alongside started mapping elsewhere)
            for rid in recording_ids:
                recordings.append({'question_number': None, 'recording_id': rid})
        else:
            # try reading from interview_row.recording_json.started_recordings
            rjson = interview_row.recording_json or {}
            started = rjson.get('started_recordings') if isinstance(rjson, dict) else None
            if started and isinstance(started, list):
                for item in started:
                    if isinstance(item, dict) and item.get('recording_id'):
                        recordings.append({'question_number': item.get('question_number'), 'recording_id': item.get('recording_id')})

        # If question filter provided, filter recordings list accordingly
        if question_id is not None or question_ids:
            wanted = set()
            if question_id is not None:
                try:
                    wanted.add(int(question_id))
                except Exception:
                    # keep as string if not int
                    wanted.add(str(question_id))
            if question_ids and isinstance(question_ids, (list, tuple)):
                for q in question_ids:
                    try:
                        wanted.add(int(q))
                    except Exception:
                        wanted.add(str(q))

            filtered = []
            for rec in recordings:
                qn = rec.get('question_number')
                if qn in wanted or (isinstance(qn, int) and qn in wanted) or (isinstance(qn, str) and qn in wanted):
                    filtered.append(rec)

            recordings = filtered

        if not recordings:
            return JsonResponse({"ok": False, "message": "No recordings found to download"}, status=200)

        # base = getattr(settings, 'BASE_DIR', os.getcwd())
        # uploads_root = os.path.join(base, 'static', 'uploads')
        base = settings.MEDIA_ROOT
        uploads_root = os.path.join(base, 'static', 'uploads')
        zoho_dir = os.path.join(uploads_root, str(zoho_lead))
        raw_dir = os.path.join(zoho_dir, 'raw')
        os.makedirs(raw_dir, exist_ok=True)

        # Enqueue background job to perform downloads using Django Q
        try:
            from django_q.tasks import async_task
        except Exception as e:
            return JsonResponse({"ok": False, "message": "django_q_not_available", "error": str(e)}, status=500)

        # pass Daily API key optionally from settings
        daily_api_key = getattr(settings, 'DAILY_API_KEY', None)

        # Queue the job. Use string path to avoid circular imports.
        job_args = [zoho_lead, recording_ids, question_id, question_ids, interview_id, daily_api_key]
        async_task('api.tasks.download_recordings_job', *job_args)

        return JsonResponse({"ok": True, "queued": True, "message": "download_job_queued"}, status=202)

    except Exception as e:
        print(f"[download_recordings] Exception: {e}")
        return JsonResponse({"ok": False, "error": str(e)}, status=500)