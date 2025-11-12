# studentpanel/tasks.py
import logging
from celery import shared_task, group, chord
from django.conf import settings

logger = logging.getLogger(__name__)

# Import your existing merge function (ensure correct path)
# from .video_merge_handler import merge_videos, get_all_video_files_for_lead, chunk_list, ffmpeg_concat
from .video_merge_handler import merge_videos

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def merge_videos_task(self, zoho_lead_id, interview_link_count=None):
    """
    Simple Celery wrapper that calls your merge_videos() function.
    This preserves your existing logic exactly.
    """
    logger.info("[CELERY] merge_videos_task start for %s", zoho_lead_id)
    try:
        result = merge_videos(zoho_lead_id, interview_link_count)
        logger.info("[CELERY] merge_videos_task completed for %s -> %s", zoho_lead_id, result)
        return {"status": "ok", "result": result}
    except Exception as exc:
        logger.exception("[CELERY] merge_videos_task failed for %s", zoho_lead_id)
        # re-raise to allow retry (autoretry_for will handle it)
        raise

# ---- Optional: Chunked merge pattern for parallel speed-up ----
# If you have many videos (e.g., 12-18), chunk them and merge chunks in parallel.
# NOTE: You need helper functions: get_all_video_files_for_lead(zoho_lead_id)
# and a merge_chunk task that merges a small list into intermediate file.
@shared_task(bind=True)
def merge_chunk(self, zoho_lead_id, chunk_index, file_list):
    """
    Merge one chunk (list of absolute file paths) into an intermediate file.
    Returns the intermediate file path.
    """
    uploads_folder = os.path.join(settings.UPLOADS_FOLDER, zoho_lead_id)  # or replicate your own logic
    out_path = os.path.join(uploads_folder, f"chunk_{chunk_index}_merged.webm").replace("\\", "/")
    logger.info("Merging chunk %s for %s into %s", chunk_index, zoho_lead_id, out_path)
    # use your ffmpeg concat helper (ffmpeg_concat defined in video_merge_handler)
    ffmpeg_concat(file_list, out_path)
    return out_path

@shared_task(bind=True)
def concat_chunks(self, chunk_files, zoho_lead_id):
    """
    Final concatenation of chunk files into single merged_video.webm
    """
    uploads_folder = os.path.join(settings.UPLOADS_FOLDER, zoho_lead_id)
    output_path = os.path.join(uploads_folder, "merged_video.webm").replace("\\", "/")
    logger.info("Concatenating chunks for %s -> %s", zoho_lead_id, output_path)
    ffmpeg_concat(chunk_files, output_path)
    return output_path

def start_chunked_merge(zoho_lead_id, chunk_size=6):
    """
    Kick off chunked merge: splits file list and runs chord(group(...), concat_chunks)
    """
    file_list = get_all_video_files_for_lead(zoho_lead_id)  # implement in video_merge_handler
    chunks = list(chunk_list(file_list, chunk_size))

    # build group of merge_chunk tasks
    grp = group(merge_chunk.s(zoho_lead_id, idx, chunk) for idx, chunk in enumerate(chunks))
    # when group finished -> concat_chunks will run with list of results
    # chord(grp)(concat_chunks.s(zoho_lead_id))  # alternative
    # return chord(grp)(concat_chunks.s(zoho_lead_id))
    # If you prefer chain:
    return chord(grp)(concat_chunks.s(zoho_lead_id))
