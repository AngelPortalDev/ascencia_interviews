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
    uploads_root = os.path.join(base, 'static', 'uploads')

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
    """Background job to download Daily.co recordings sequentially for a zoho_lead.

    - `recording_ids`: optional list of recording ids to download. If not
      provided, function attempts to read from the interview_row.recording_json
      started_recordings.
    - `question_id` / `question_ids` can be used to filter which recordings to download.
    - `daily_api_key` if provided will be used; otherwise the function expects
      `DAILY_API_KEY` to be available via settings or environment.
    """
    logger.info(
    "[download_recordings_job] START zoho=%s interview_id=%s recording_ids=%s",
    zoho_lead, interview_id, bool(recording_ids)
)

    if daily_api_key:
        DAILY_API_KEY = daily_api_key
    else:
        DAILY_API_KEY = getattr(settings, 'DAILY_API_KEY', None)

    if not zoho_lead and not interview_id and not recording_ids:
        return {'ok': False, 'error': 'missing_identifiers'}

    # Resolve interview row
    interview_row = None
    if interview_id:
        interview_row = StudentInterviewLink.objects.filter(id=interview_id).first()
        zoho_lead = zoho_lead or (getattr(interview_row, 'zoho_lead_id', None) if interview_row else None)
    elif zoho_lead:
        interview_row = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead).order_by('-id').first()
    
    logger.info(
    "[download_recordings_job] interview_row resolved=%s zoho=%s",
    bool(interview_row),
    zoho_lead
)

    if not zoho_lead:
        return {'ok': False, 'error': 'zoho_lead_required'}

    # Build recordings list
    recordings = []
    if recording_ids and isinstance(recording_ids, (list, tuple)):
        for rid in recording_ids:
            recordings.append({'question_number': None, 'recording_id': rid})
    else:
        if interview_row:
            rjson = interview_row.recording_json or {}
            started = rjson.get('started_recordings') if isinstance(rjson, dict) else None
            if started and isinstance(started, list):
                for item in started:
                    if isinstance(item, dict) and item.get('recording_id'):
                        recordings.append({'question_number': item.get('question_number'), 'recording_id': item.get('recording_id')})

    # Apply question filters
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

        recordings = [r for r in recordings if (r.get('question_number') in wanted or (isinstance(r.get('question_number'), int) and r.get('question_number') in wanted))]

    if not recordings:
        return {'ok': False, 'message': 'no_recordings_found'}
    
    logger.info(
    "[download_recordings_job] recordings_to_download count=%s details=%s",
    len(recordings),
    [(r.get('question_number'), r.get('recording_id')) for r in recordings]
)


    base, videos_dir = _ensure_dirs(zoho_lead)



    headers_daily = {'Authorization': f'Bearer {DAILY_API_KEY}', 'Content-Type': 'application/json'}
    downloaded = []

    for rec in recordings:
        rid = rec.get('recording_id')
        qnum = rec.get('question_number')
        logger.info(
    "[download_recordings_job] requesting access-link rid=%s",
    rid
)

        if not rid:
            continue

        dl_url = None
        # Primary: request access-link (provides a time-limited S3 download URL)
        try:
            access_res = requests.get(
                f"https://api.daily.co/v1/recordings/{rid}/access-link",
                headers=headers_daily,
                timeout=15
            )

            logger.info(
                "[download_recordings_job] access-link response rid=%s status=%s body=%s",
                rid,
                access_res.status_code,
                access_res.text[:300]
            )

            if access_res.status_code == 200:
                ar = access_res.json()
                # Prefer explicit download_link; fall back to other keys
                dl_url = ar.get('download_link') or ar.get('download_url') or ar.get('url')
                # If access-link provides s3_key, use it for nicer filename
                s3_key = ar.get('s3_key') or ar.get('data', {}).get('s3_key')
            else:
                # fallback to recording metadata if access-link not available
                s3_key = None
                meta_res = requests.get(f"https://api.daily.co/v1/recordings/{rid}", headers=headers_daily, timeout=15)
                if meta_res.status_code == 200:
                    m = meta_res.json()
                    dl_url = m.get('download_link') or m.get('download_url') or m.get('url') or m.get('data', {}).get('download_link')
                    s3_key = m.get('s3_key') or m.get('data', {}).get('s3_key')
                    logger.warning(
                        "[download_recordings_job] access-link failed rid=%s status=%s",
                        rid,
                        access_res.status_code
                    )

            # log helpful debug info
            # print(f"[download_recordings_job] access-link status for {rid}: {getattr(access_res, 'status_code', None)} dl_url={'SET' if dl_url else 'NONE'}")
        except Exception as e:
            # print(f"[download_recordings_job] access-link error for {rid}: {e}")
            logger.exception(
            "[download_recordings_job] access-link exception rid=%s",
            rid
        )

            dl_url = None
            s3_key = None

        if not dl_url:
            downloaded.append({'recording_id': rid, 'question_number': qnum, 'url': None, 'error': 'no_download_url'})
            continue

        try:
            # Prefer using s3_key (gives clean filename), else parse URL path
            if 's3_key' in locals() and s3_key:
                parsed_name = os.path.basename(s3_key)
            else:
                parsed_name = os.path.basename(dl_url.split('?')[0]) if dl_url else None

            # Try to extract an epoch millisecond timestamp from s3_key or parsed_name
            timestamp_ms = None
            if parsed_name and re.fullmatch(r"\d{10,13}", parsed_name):
                timestamp_ms = int(parsed_name)
            else:
                # look for a 10-13 digit number inside the parsed_name
                if parsed_name:
                    m = re.search(r"(\d{10,13})", parsed_name)
                    if m:
                        timestamp_ms = int(m.group(1))

            if timestamp_ms:
                try:
                    dt = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
                    ts = dt.strftime("%Y-%m-%dT%H-%M-%S")
                except Exception:
                    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
            else:
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

            qpart = str(qnum) if qnum else str(rid)
            # final filename format: interview_video_<zoho>_<questionid|rid>_<timestamp>.mp4
            fname = f"interview_video_{zoho_lead}_{qpart}_{ts}.mp4"
        except Exception:
            fname = f"interview_video_{zoho_lead}_{qnum or rid}_{int(time.time())}.mp4"

        # Save final videos into interview_videos (user requested location)
        dest_path = os.path.join(videos_dir, fname)
        logger.info(
    "[download_recordings_job] downloading rid=%s q=%s filename=%s",
    rid, qnum, fname
)
        try:
            with requests.get(dl_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as fh:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            fh.write(chunk)
            logger.info(
                "[download_recordings_job] download success rid=%s path=%s",
                rid, dest_path
            )
            relpath = os.path.relpath(dest_path, base)
            downloaded.append({'recording_id': rid, 'question_number': qnum, 'url': dl_url, 'raw_path': relpath, 'name': fname})

            # Map to StudentInterviewAnswers - try to derive question number if missing,
            # then update-or-create (when qnum available) or create a new row otherwise.
            try:
                resolved_qnum = qnum
                # attempt to resolve question_number from interview_row.recording_json
                if not resolved_qnum and interview_row:
                    try:
                        rjson = interview_row.recording_json or {}
                        started = rjson.get('started_recordings') if isinstance(rjson, dict) else None
                        if started and isinstance(started, list):
                            for item in started:
                                if isinstance(item, dict) and item.get('recording_id') == rid:
                                    resolved_qnum = item.get('question_number')
                                    break
                    except Exception:
                        resolved_qnum = resolved_qnum

                if resolved_qnum:
                    # use update_or_create so we don't duplicate rows for same zoho+question
                    obj, created = StudentInterviewAnswers.objects.update_or_create(
                        zoho_lead_id=zoho_lead,
                        question_id=resolved_qnum,
                        defaults={'video_path': relpath}
                    )
                    # print(f"[download_recordings_job] StudentInterviewAnswers {'created' if created else 'updated'} for zoho={zoho_lead} q={resolved_qnum}")
                    logger.info(
                    "[download_recordings_job] StudentInterviewAnswers %s zoho=%s q=%s",
                    "created" if created else "updated",
                    zoho_lead,
                    resolved_qnum
                )

                else:
                    # No question number available: create a new answer row to record the video path
                    obj = StudentInterviewAnswers.objects.create(
                        zoho_lead_id=zoho_lead,
                        question_id=None,
                        video_path=relpath
                    )
                    # print(f"[download_recordings_job] StudentInterviewAnswers created (no qnum) id={obj.id} zoho={zoho_lead}")
                    logger.warning(
                        "[download_recordings_job] answer saved without question_number zoho=%s rid=%s",
                        zoho_lead,
                        rid
                    )


            except Exception as e:
                print(f"[download_recordings_job] failed to save/create answer row for {rid}: {e}")

        except Exception as e:
            downloaded.append({'recording_id': rid, 'question_number': qnum, 'url': dl_url, 'error': str(e)})

    # update interview_row.recording_files
    try:
        if interview_row:
            prior = interview_row.recording_files or []
            if not isinstance(prior, list):
                prior = []
            prior.extend(downloaded)
            interview_row.recording_files = prior
            interview_row.process_status = 'downloaded' if downloaded else interview_row.process_status
            # persist status and files explicitly
            try:
                interview_row.save(update_fields=['recording_files', 'process_status'])
            except Exception:
                # fallback to full save if update_fields not supported
                interview_row.save()

            # trigger downstream merge/transcribe flow via async task when status is 'downloaded'
            try:
                if interview_row.process_status == 'downloaded':
                    try:
                        from django_q.tasks import async_task
                        async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead, interview_row.interview_link_count)
                        # print(f"[download_recordings_job] enqueued merge_videos for zoho={zoho_lead} interview_link_count={interview_row.interview_link_count}")
                        logger.info(
                            "[download_recordings_job] merge_videos enqueued zoho=%s link_count=%s",
                            zoho_lead,
                            interview_row.interview_link_count
                        )

                    except Exception as e:
                        print(f"[download_recordings_job] failed to enqueue merge_videos: {e}")
            except Exception as e:
                print(f"[download_recordings_job] failed to trigger merge: {e}")
    except Exception:
        pass

    return {'ok': True, 'downloaded': downloaded}
