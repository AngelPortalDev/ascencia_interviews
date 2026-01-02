import os
import time
import requests
import re
from datetime import datetime, timezone
from django.conf import settings
from sklearn import base

from studentpanel.models.interview_process_model import Students
from studentpanel.models.student_Interview_status import StudentInterview
from studentpanel.models.student_interview_answer import StudentInterviewAnswers

from django.conf import settings

from studentpanel.models.interview_link import StudentInterviewLink
# import merge processor to trigger after download
try:
    from studentpanel.observer.dailycomerging import process_interview_by_zoho
except Exception:
    process_interview_by_zoho = None


import logging

logger = logging.getLogger('zoho_webhook_logger')



def _ensure_dirs(zoho_lead):
    # base = getattr(settings, 'BASE_DIR', os.getcwd())
    # uploads_root = os.path.join(base, 'static', 'uploads')
    base = settings.MEDIA_ROOT
    uploads_root = os.path.join(base, 'uploads')

    videos_dir = os.path.join(uploads_root, 'interview_videos', str(zoho_lead))

    os.makedirs(videos_dir, exist_ok=True)
    return base, videos_dir


def get_assigned_questions_count(interview_row):
    common_ids = interview_row.assigned_question_ids
    course_ids = interview_row.assigned_course_question_ids

    common_count = len([i for i in common_ids.split(",") if i.strip()]) if common_ids else 0
    course_count = len([i for i in course_ids.split(",") if i.strip()]) if course_ids else 0

    return common_count + course_count
def get_recorded_questions_count(interview_row):
    rjson = interview_row.recording_json or {}
    started = rjson.get("started_recordings")

    if isinstance(started, list):
        # question_number unique count
        return len({str(i.get("question_number")) for i in started if i.get("question_number") is not None})

    return 0


def download_recordings_job(zoho_lead, recording_ids=None, question_id=None, question_ids=None, interview_id=None, daily_api_key=None):
    """Background job to download Daily.co recordings sequentially for a zoho_lead."""
    logger.info(
        "download_recordings_job started | zoho_lead=%s interview_id=%s recording_ids=%s question_id=%s question_ids=%s",
        zoho_lead, interview_id, recording_ids, question_id, question_ids
    )

    if daily_api_key:
        DAILY_API_KEY = daily_api_key
        logger.info("Using DAILY_API_KEY passed as argument")
    else:
        DAILY_API_KEY = getattr(settings, 'DAILY_API_KEY', None)
        logger.info("Using DAILY_API_KEY from settings")

    if not zoho_lead and not interview_id and not recording_ids:
        logger.error("Missing identifiers: zoho_lead, interview_id, recording_ids all empty")
        return {'ok': False, 'error': 'missing_identifiers'}

    # Resolve interview row
    interview_row = None
    try:
        if interview_id:
            interview_row = StudentInterviewLink.objects.filter(id=interview_id).first()
            zoho_lead = zoho_lead or (getattr(interview_row, 'zoho_lead_id', None) if interview_row else None)
            logger.info("Interview row resolved via interview_id=%s", interview_id)
        elif zoho_lead:
            interview_row = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead).order_by('-id').first()
            logger.info("Interview row resolved via zoho_lead=%s", zoho_lead)
    except Exception:
        logger.exception("Failed while resolving interview_row")

    if not zoho_lead:
        logger.error("zoho_lead could not be resolved")
        return {'ok': False, 'error': 'zoho_lead_required'}

    # Build recordings list
    recordings = []
    try:
        if recording_ids and isinstance(recording_ids, (list, tuple)):
            for rid in recording_ids:
                recordings.append({'question_number': None, 'recording_id': rid})
            logger.info("Using explicit recording_ids (%d)", len(recording_ids))
        else:
            if interview_row:
                rjson = interview_row.recording_json or {}
                started = rjson.get('started_recordings') if isinstance(rjson, dict) else None
                if started and isinstance(started, list):
                    for item in started:
                        if isinstance(item, dict) and item.get('recording_id'):
                            recordings.append({
                                'question_number': item.get('question_number'),
                                'recording_id': item.get('recording_id')
                            })
                    logger.info("Loaded %d recordings from interview_row.recording_json", len(recordings))
    except Exception:
        logger.exception("Failed while building recordings list")

    # Apply question filters
    try:
        wanted = None
        if question_id is not None or question_ids:
            wanted = set()
            if question_id is not None:
                try:
                    wanted.add(int(question_id))
                except Exception:
                    wanted.add(str(question_id))
            if question_ids and isinstance(question_ids, (list, tuple)):
                for q in question_ids:
                    try:
                        wanted.add(int(q))
                    except Exception:
                        wanted.add(str(q))

            before = len(recordings)
            recordings = [
                r for r in recordings
                if (r.get('question_number') in wanted or
                    (isinstance(r.get('question_number'), int) and r.get('question_number') in wanted))
            ]
            logger.info("Question filter applied | before=%d after=%d", before, len(recordings))
    except Exception:
        logger.exception("Failed while applying question filters")

    if not recordings:
        logger.warning("No recordings found after filtering")
        return {'ok': False, 'message': 'no_recordings_found'}

    base, videos_dir = _ensure_dirs(zoho_lead)
    logger.info("Directories ensured | base=%s videos_dir=%s", base, videos_dir)

    headers_daily = {'Authorization': f'Bearer {DAILY_API_KEY}', 'Content-Type': 'application/json'}
    downloaded = []

    for rec in recordings:
        rid = rec.get('recording_id')
        qnum = rec.get('question_number')

        if not rid:
            logger.warning("Skipping empty recording_id entry")
            continue

        logger.info("Processing recording_id=%s question_number=%s", rid, qnum)

        dl_url = None
        s3_key = None

        try:
            access_res = requests.get(
                f"https://api.daily.co/v1/recordings/{rid}/access-link",
                headers=headers_daily,
                timeout=15
            )
            logger.info("Daily access-link response | rid=%s status=%s", rid, access_res.status_code)

            if access_res.status_code == 200:
                ar = access_res.json()
                dl_url = ar.get('download_link') or ar.get('download_url') or ar.get('url')
                s3_key = ar.get('s3_key') or ar.get('data', {}).get('s3_key')
            else:
                meta_res = requests.get(
                    f"https://api.daily.co/v1/recordings/{rid}",
                    headers=headers_daily,
                    timeout=15
                )
                logger.warning("Fallback to metadata API | rid=%s status=%s", rid, meta_res.status_code)
                if meta_res.status_code == 200:
                    m = meta_res.json()
                    dl_url = m.get('download_link') or m.get('download_url') or m.get('url') or m.get('data', {}).get('download_link')
                    s3_key = m.get('s3_key') or m.get('data', {}).get('s3_key')

        except Exception:
            logger.exception("Daily API failure for recording_id=%s", rid)

        if not dl_url:
            logger.error("No download URL resolved | recording_id=%s", rid)
            downloaded.append({'recording_id': rid, 'question_number': qnum, 'url': None, 'error': 'no_download_url'})
            continue

        try:
            parsed_name = os.path.basename(s3_key) if s3_key else os.path.basename(dl_url.split('?')[0])
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
            qpart = str(qnum) if qnum else str(rid)
            fname = f"interview_video_{zoho_lead}_{qpart}_{ts}.mp4"
            dest_path = os.path.join(videos_dir, fname)

            logger.info("Downloading recording | rid=%s -> %s", rid, dest_path)

            with requests.get(dl_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as fh:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            fh.write(chunk)

            relpath = os.path.relpath(dest_path, base)
            downloaded.append({
                'recording_id': rid,
                'question_number': qnum,
                'url': dl_url,
                'raw_path': relpath,
                'name': fname
            })

            logger.info("Download successful | rid=%s saved=%s", rid, relpath)

        except Exception:
            logger.exception("Failed downloading or saving recording | rid=%s", rid)
            downloaded.append({'recording_id': rid, 'question_number': qnum, 'url': dl_url, 'error': 'download_failed'})

    # Persist interview status
    try:
        if interview_row:
            prior = interview_row.recording_files or []
            if not isinstance(prior, list):
                prior = []

            prior.extend(downloaded)
            interview_row.recording_files = prior
            interview_row.process_status = 'downloaded' if downloaded else interview_row.process_status
            interview_row.save(update_fields=['recording_files', 'process_status'])

            logger.info("Interview row updated | zoho_lead=%s status=%s",
                        zoho_lead, interview_row.process_status)

            if interview_row.process_status == 'downloaded':
                try:
                    from django_q.tasks import async_task
                    async_task(
                        "studentpanel.observer.video_merge_handler.merge_videos",
                        zoho_lead,
                        interview_row.interview_link_count
                    )
                    logger.info("merge_videos task enqueued | zoho_lead=%s", zoho_lead)
                except Exception:
                    logger.exception("Failed to enqueue merge_videos task")

    except Exception:
        logger.exception("Failed updating interview_row or triggering merge")

    logger.info("download_recordings_job completed | zoho_lead=%s downloaded=%d",
                zoho_lead, len(downloaded))

    return {'ok': True, 'downloaded': downloaded}

