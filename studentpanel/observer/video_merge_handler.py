import os
import subprocess
import requests
from django.conf import settings
from django.contrib.auth.models import User
from studentpanel.models.interview_process_model import Students
from adminpanel.utils import send_email
from django.db.models.signals import post_save
from django.dispatch import receiver
from studentpanel.models.student_interview_answer import StudentInterviewAnswers
from django_q.tasks import async_task
import logging
from django.core.mail import EmailMultiAlternatives
import mimetypes
from studentpanel.models.student_Interview_status import StudentInterview
from studentpanel.models.interview_link import StudentInterviewLink
import time
from adminpanel.models.common_question import CommonQuestion
from adminpanel.models.question import Question
logging.basicConfig(level=logging.INFO)
import uuid
import json
import whisper
import warnings
from django.utils.html import escape
import re
from django_q.tasks import async_task, schedule
from django.utils.timezone import now, timedelta
import torch
from django.conf import settings

from django_q.models import Schedule
from adminpanel.helper.email_branding import get_email_branding

from html import escape
from concurrent.futures import ThreadPoolExecutor, as_completed
import whisper

logger = logging.getLogger(__name__)
import subprocess
import textwrap
from PIL import ImageFont
import tempfile

import math

import logging

logger = logging.getLogger('zoho_webhook_logger')

def get_uploads_folder():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    logging.info("project_root: %s", project_root)
    uploads_folder = os.path.join(project_root,"static","uploads", "interview_videos")
    logging.info("uploads folder text: %s", uploads_folder)
    return uploads_folder.replace("\\", "/")


def convert_video(input_path, output_path, target_format):
    import subprocess
    import logging
    import imageio_ffmpeg
    import warnings

    logging.info("output_path: %s", output_path)
    logging.info("target_format path: %s", target_format)

    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    logging.info("Using FFmpeg: %s", FFMPEG_PATH)
    logging.info("Input path: %s", input_path)
    logging.info("Output path: %s", output_path)

    if target_format == "webm":
        command = (
            FFMPEG_PATH,
            "-y",
            "-fflags", "+genpts",
            "-i", input_path,
            "-vf", "scale=640:480:flags=lanczos,fps=30",
            "-r", "30",
            "-vsync", "cfr",
            "-video_track_timescale", "30000",
            "-c:v", "libvpx",
            "-b:v", "2M",
            "-maxrate", "2M",
            "-bufsize", "4M",
            "-cpu-used", "0",
            "-deadline", "good",
            "-pix_fmt", "yuv420p",
            "-c:a", "libopus",
            "-b:a", "128k",
            "-ar", "48000",
            "-ac", "2",
            "-af", "aresample=async=1000",
            "-movflags", "+faststart",
            output_path,
        )
        logging.info("FFmpeg command1: %s", " ".join(command))

    elif target_format == "mp4":
        command = f'ffmpeg -i "{input_path}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
        logging.info("FFmpeg command2: %s", command)

    elif target_format == "mov":
        command = f'ffmpeg -i "{input_path}" -c:v prores -c:a pcm_s16le "{output_path}"'

    else:
        raise ValueError(f"Unsupported format: {target_format}")

    try:
        if isinstance(command, (list, tuple)):
            subprocess.run(command, check=True)
        else:
            subprocess.run(command, shell=True, check=True)

    except subprocess.CalledProcessError:
        logger.error("FFmpeg failed for file: %s", input_path, exc_info=True)
        raise

    except Exception:
        logger.error("Unexpected error in convert_video()", exc_info=True)
        raise


warnings.filterwarnings(
    "ignore",
    message="FP16 is not supported on CPU; using FP32 instead"
)




def transcribe_complete_video(video_path):
    if not os.path.exists(video_path):
        print("❌ File not found:", video_path)
        return None

    print("📦 Loading Whisper model (small, fast)...")
    model = whisper.load_model("small")

    print("🧠 Transcribing full video...")
    result = model.transcribe(
        video_path,
        language="en",
        word_timestamps=False,
        verbose=False,
        task="transcribe",
    )

    # Clean output
    full_text = " ".join(result['text'].strip().split())

    # Save to text file
    transcript_txt_path = os.path.splitext(video_path)[0] + "_transcript.txt"
    with open(transcript_txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"✅ Transcript saved: {transcript_txt_path}")
    return transcript_txt_path


# CHUNK_SIZE = 5 * 1024 * 1024   # 5 MB

# def upload_to_bunnystream(video_path):
#     video_name = os.path.basename(video_path)
#     library_id = settings.BUNNY_STREAM_LIBRARY_ID
#     api_key = settings.BUNNY_STREAM_API_KEY

#     logging.info(f"Uploading to Bunny Stream (CHUNK MODE): {video_name}")

#     # 1️⃣ Create video entry
#     create_url = f"https://video.bunnycdn.com/library/{library_id}/videos"
#     create_headers = {
#         "AccessKey": api_key,
#         "Content-Type": "application/json"
#     }
#     create_res = requests.post(create_url, json={"title": video_name}, headers=create_headers)

#     if create_res.status_code != 200:
#         logging.error(f"Failed to create Bunny video entry: {create_res.text}")
#         return None

#     video_id = create_res.json().get("guid")
#     if not video_id:
#         logging.error("No video GUID returned from Bunny Stream")
#         return None

#     logging.info(f"Created Bunny Video GUID: {video_id}")

#     # 2️⃣ Upload in chunks
#     upload_url = f"https://video.bunnycdn.com/library/{library_id}/videos/{video_id}"

#     file_size = os.path.getsize(video_path)
#     total_chunks = math.ceil(file_size / CHUNK_SIZE)

#     with open(video_path, "rb") as f:
#         for chunk_index in range(total_chunks):
#             start = chunk_index * CHUNK_SIZE
#             end = min(start + CHUNK_SIZE - 1, file_size - 1)
#             chunk_data = f.read(CHUNK_SIZE)

#             logging.info(f"Uploading chunk {chunk_index+1}/{total_chunks}  ({start}-{end})")

#             headers = {
#                 "AccessKey": api_key,
#                 "Content-Type": "application/octet-stream",
#                 "Content-Range": f"bytes {start}-{end}/{file_size}"
#             }

#             response = requests.put(upload_url, headers=headers, data=chunk_data)

#             if response.status_code not in (200, 201):
#                 logging.error(f"Chunk upload failed: {response.text}")
#                 return None

#     logging.info("🔥 Chunk upload completed successfully!")
#     return video_id


def upload_to_bunnystream(video_path):
    video_name = os.path.basename(video_path)
    logging.info("video_name: %s", video_name)
    logging.info("bunny stream library id: %s", settings.BUNNY_STREAM_LIBRARY_ID)
    logging.info("bunny stream library api key : %s", settings.BUNNY_STREAM_API_KEY)

    create_url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos"
    headers = {
        "AccessKey": settings.BUNNY_STREAM_API_KEY,
        "Content-Type": "application/json"
    }
    logging.info("bunny stream library create_url : %s", create_url)

    response = requests.post(create_url, json={"title": video_name}, headers=headers)
    logging.info("bunny stream library response : %s", response)
    video_id = response.json().get("guid")
    logging.info("bunny stream library video_id : %s", video_id)
    if not video_id:
        return "Error: Video GUID not received."

    upload_url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos/{video_id}"
    logging.info("bunny stream library upload_url : %s", upload_url)
    headers = {
        "AccessKey": settings.BUNNY_STREAM_API_KEY,
        "Content-Type": "application/octet-stream"
    }

    with open(video_path, "rb") as video_file:
        logging.info("bunny stream library video_file : %s", video_file)
        upload_response = requests.put(upload_url, headers=headers, data=video_file)
        logging.info("bunny stream library upload_response : %s", upload_response)

    if upload_response.status_code == 201:
         return f"Error uploading video: {upload_response.text}"
    else:
        return video_id
    
def get_duration(file_path):
    # FFMPEG_PROBE = '/usr/bin/ffprobe'
    # FFMPEG_PROBE = "C:/ffmpeg/bin/ffprobe.exe"
    cmd = [
        settings.FFMPEG_PROBE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10)
        duration_str = output.decode().strip()
        if not duration_str or duration_str.lower() == 'n/a':
            raise ValueError("Duration not available")
        duration = float(duration_str)
        return duration
    except Exception as e:
        logging.warning(f"Duration check failed for {file_path}: {e}. Using fallback duration 2.0s")
        return 2.0

def wrap_text_pixels(text, font_path, fontsize, max_width_px):
    font = ImageFont.truetype(font_path, fontsize)
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(current_line.split()) >= 16:
            lines.append(current_line)
            current_line = word
            continue
        bbox = font.getbbox(test_line)
        w = bbox[2] - bbox[0]

        if w <= max_width_px:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            word_bbox = font.getbbox(word)
            word_width = word_bbox[2] - word_bbox[0]
            if word_width > max_width_px:
                split_word = [word[i:i+10] for i in range(0, len(word), 10)]
                lines.extend(split_word[:-1])
                current_line = split_word[-1]
            else:
                current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def save_wrapped_text_file(text, font_path, fontsize, max_width_px):
    wrapped_lines = wrap_text_pixels(text, font_path, fontsize, max_width_px)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    tmp_file.write("\n".join(wrapped_lines))
    tmp_file.close()

    original_path = tmp_file.name
    # Correct FFmpeg path: double backslash before colon + forward slashes for rest
    if os.name == "nt":   # Windows
        path = original_path
        if ":" in path:
            drive, rest = path.split(":", 1)
            # ffmpeg_path = original_path
            rest_clean = rest.replace("\\", "/")
            ffmpeg_path = f"{drive}\\\\:{rest_clean}"
        else:
            ffmpeg_path = path.replace("\\", "/")
    else:                 # Linux (cPanel)
        ffmpeg_path = original_path  # NO escaping needed

    return original_path,ffmpeg_path


def generate_question_video(text, output_path, duration=2, fontsize=12, max_width_px=500):
    # Font path with DOUBLE backslash before colon for FFmpeg
    font_path = settings.FONT_PATH  # e.g., "C:/Windows/Fonts/arial.ttf"
    ffmpeg_path = settings.FFMPEG_PATH
    # font_path_ffmpeg = font_path.replace(":", "\\\\").replace("\\", "/")

    # Generate wrapped text file
    original_path,text_file_path = save_wrapped_text_file(text, font_path, fontsize, max_width_px)

    # Drawtext exactly like your working command
    drawtext = (
        f"drawtext=fontfile={font_path}:"
        f"textfile={text_file_path}:"
        f"fontcolor=white:fontsize={fontsize}:line_spacing=6:"
        "x=(w-text_w)/2:y=(h-text_h)/2:"
        "fix_bounds=1:box=1:boxcolor=black@0.4:boxborderw=20"
    )

    # command = (
    #     f'"C:/ffmpeg/bin/ffmpeg.exe" -f lavfi -i color=c=black:s=640x360:d={duration} '
    #     f'-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 '
    #     f'-vf "{drawtext}" -shortest '
    #     f'-c:v libvpx -b:v 1M -c:a libopus -ar 48000 -ac 2 '
    #     f'-y "{output_path}"'
    # )
    command = (
        f'"{ffmpeg_path}" -f lavfi -i color=c=black:s=640x360:d={duration} '
        f'-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 '
        f'-vf "{drawtext}" -shortest '
        f'-c:v libvpx -b:v 1M -c:a libopus -ar 48000 -ac 2 '
        f'-y "{output_path}"'
    )

    print("Running FFmpeg command:", command)
    subprocess.run(command, shell=True, check=True)

    os.remove(original_path)

def wait_for_complete_files(folder, min_files=1, stable_duration=5, timeout=30):
    start = time.time()
    last_sizes = {}
    stable_start = None

    while time.time() - start < timeout:
        video_files = [
            f for f in os.listdir(folder)
            if f.endswith((".webm", ".mp4", ".mov"))
        ]

        if len(video_files) < min_files:
            time.sleep(1)
            continue

        current_sizes = {
            f: os.path.getsize(os.path.join(folder, f))
            for f in video_files
        }

        if current_sizes == last_sizes:
            if stable_start is None:
                stable_start = time.time()
            elif time.time() - stable_start >= stable_duration:
                return sorted(video_files, key=lambda x: os.path.getctime(os.path.join(folder, x)))
        else:
            stable_start = None

        last_sizes = current_sizes
        time.sleep(1)

    raise TimeoutError(f"Files not stable in {folder} after {timeout} seconds.")


    # return video_i
def get_codecs(video_path):
    # FFMPEG_PROBE = 'C:/ffmpeg/bin/ffprobe.exe'
    # FFMPEG_PROBE = '/usr/bin/ffprobe'

    cmd_video = [
        settings.FFMPEG_PROBE, '-v', 'error',
        '-select_streams', 'v:0', '-show_entries', 'stream=codec_name',
        '-of', 'json', video_path
    ]
    result_video = subprocess.run(cmd_video, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    video_codec = json.loads(result_video.stdout)["streams"][0]["codec_name"].lower()

    cmd_audio = [
        settings.FFMPEG_PROBE, '-v', 'error',
        '-select_streams', 'a:0', '-show_entries', 'stream=codec_name',
        '-of', 'json', video_path
    ]
    result_audio = subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    audio_codec = json.loads(result_audio.stdout)["streams"][0]["codec_name"].lower()

    return video_codec, audio_codec


def is_video_valid(video_path):
    # FFMPEG_PROBE = 'C:/ffmpeg/bin/ffprobe.exe'
    # FFMPEG_PROBE = '/usr/bin/ffprobe'
    try:
        cmd = [
            settings.FFMPEG_PROBE, "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=avg_frame_rate,duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=5)
        avg_fps, duration = output.decode().strip().splitlines()

        if avg_fps in ("0/0", "", "N/A") or duration in ("N/A", "", None):
            return False
        return True
    except Exception as e:
        logging.warning(f"Invalid video structure, will re-encode: {video_path} | Error: {e}")
        return False

# def build_qa_blocks_with_paths(questions, converted_files):
#     qa_blocks = []
#     total_pairs = len(converted_files) // 2  # floor division to avoid IndexError
#     for i in range(total_pairs):
#         q_file = converted_files[i * 2]
#         a_file = converted_files[i * 2 + 1]

#         # Safety check: skip if missing or 0-byte
#         if not os.path.exists(a_file) or os.path.getsize(a_file) == 0:
#             logging.warning("Skipping Q&A block: missing answer file: %s", a_file)
#             continue
#         if not os.path.exists(q_file) or os.path.getsize(q_file) == 0:
#             logging.warning("Skipping Q&A block: missing question file: %s", q_file)
#             continue

#         question_text = questions[i].question if i < len(questions) else "[Unknown Question]"
#         qa_blocks.append({
#             "question": question_text,
#             "q_file": q_file,
#             "a_file": a_file
#         })
#     return qa_blocks


def build_qa_blocks_with_paths(ordered_questions, answers_qid_map, uploads_folder):
    """
    Build Q&A blocks using question IDs (NOT indices).
    
    Args:
        ordered_questions: List of question objects (CommonQuestion or Question)
        answers_qid_map: Dict mapping question_id -> StudentInterviewAnswers
        uploads_folder: Path to uploads folder
        
    Returns:
        List of dicts with: {question_id, question_text, q_file, a_file}
    """
    qa_blocks = []
    
    # Loop through questions by ID (not by index)
    for question in ordered_questions:
        question_id = question.id
        
        # Check if answer exists in database
        answer = answers_qid_map.get(question_id)
        if not answer:
            logging.warning(f"❌ No answer in DB for Question ID {question_id}")
            continue
        
        # Get answer video path from database
        answer_path = answer.video_path
        if not answer_path:
            logging.warning(f"❌ No video_path in DB for Question ID {question_id}")
            continue
        
        # Validate answer file exists on disk
        if not os.path.exists(answer_path) or os.path.getsize(answer_path) == 0:
            logging.warning(f"❌ Answer video missing/empty for Question ID {question_id}")
            continue
        
        # Find question video file
        question_filename = f"question_{question_id}_converted.webm"
        question_path = os.path.join(uploads_folder, question_filename).replace("\\", "/")
        
        # Validate question file exists
        if not os.path.exists(question_path) or os.path.getsize(question_path) == 0:
            logging.warning(f"❌ Question video missing/empty for Question ID {question_id}")
            continue
        
        # ✅ Both files exist - add to blocks with question_id
        qa_block = {
            "question_id": question_id,      # ← KEY CHANGE: Use actual ID
            "question_text": question.question,
            "q_file": question_path,
            "a_file": answer_path
        }
        qa_blocks.append(qa_block)
        
        logging.info(f"✅ Q&A pair validated - Question ID {question_id}")
    
    logging.info(f"✅ Total valid Q&A pairs: {len(qa_blocks)}")
    return qa_blocks

def merge_videos(zoho_lead_id,interview_link_count=None):
    time.sleep(10)
    logger.info("[MERGE TRIGGERED] zoho_lead_id=%s", zoho_lead_id)
    uploads_folder = os.path.join(get_uploads_folder(), zoho_lead_id)
    logging.info("uploads_folder: %s", uploads_folder)

    if not os.path.exists(uploads_folder):
        return f"Error: Folder {uploads_folder} does not exist."
    
    output_filename = "merged_video.webm"
    output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")
    if os.path.exists(output_path):
        logging.info("Merge already completed for this lead. Skipping...")
        return "Merge already completed. Skipping..."
    
    try:
        video_files = wait_for_complete_files(uploads_folder, min_files=1, stable_duration=5, timeout=30)
    except TimeoutError as e:
        return str(e)

    # Get answers and questions
        # this code for random questions with interviewlink
    try:
        interview_link = StudentInterviewLink.objects.get(
                zoho_lead_id=zoho_lead_id,
                interview_link_count=interview_link_count
            )
    except StudentInterviewLink.DoesNotExist:
        return f"Interview link not found for zoho_lead_id: {zoho_lead_id}"

    # -----------------------------
    # ✅ Fetch both question types
    # -----------------------------
    common_ids = list(map(int, interview_link.assigned_question_ids.split(","))) if interview_link.assigned_question_ids else []
    course_ids = list(map(int, interview_link.assigned_course_question_ids.split(","))) if interview_link.assigned_course_question_ids else []

    if not common_ids and not course_ids:
        return f"No assigned questions for zoho_lead_id: {zoho_lead_id}"

    # Fetch from both models
    common_qs = list(CommonQuestion.active_objects.filter(id__in=common_ids))
    course_qs = list(Question.active_objects.filter(id__in=course_ids))

    # Map by ID for quick access
    common_map = {q.id: q for q in common_qs}
    course_map = {q.id: q for q in course_qs}

    # Preserve order: common first, then course
    ordered_questions = []
    for qid in common_ids:
        if qid in common_map:
            ordered_questions.append(common_map[qid])
    for qid in course_ids:
        if qid in course_map:
            ordered_questions.append(course_map[qid])

    # -----------------------------
    # ✅ Fetch answers in order
    # -----------------------------
    answers = list(StudentInterviewAnswers.objects.filter(
        zoho_lead_id=zoho_lead_id
    ).order_by("created_at")[:len(ordered_questions)])

    if not answers:
        return f"No answers found for lead ID {zoho_lead_id}."

    if len(ordered_questions) < len(answers):
        logging.warning("Some questions missing or not matched.")


    # if len(ordered_questions) < len(answers):
    #     return f"Some question IDs are missing from CommonQuestion."

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    video_files = []

    # ----------------------------------------
# BUILD ANSWER MAP BY QUESTION ID
# ----------------------------------------
    answers_qid_map = {}

    for ans in answers:
        if ans.question_id:
            answers_qid_map[ans.question_id] = ans


    # ----------------------------------------
    # LOOP QUESTIONS IN CORRECT ORDER
    # ----------------------------------------
    for question in ordered_questions:
        qid = question.id

        # Find matching answer
        answer = answers_qid_map.get(qid)

        if not answer:
            logging.warning(f"Skipping: No answer for Question {qid}")
            continue

        answer_path = os.path.join(project_root, answer.video_path).replace("\\", "/")

        # Skip corrupted answer
        if not os.path.exists(answer_path) or os.path.getsize(answer_path) == 0:
            logging.warning(f"Skipping Question {qid}: Answer missing or 0-byte.")
            continue

        # Generate question video ONLY if answer exists
        question_filename = f"question_{qid}.webm"
        question_path = os.path.join(uploads_folder, question_filename).replace("\\", "/")

        if not os.path.exists(question_path):
            generate_question_video(
                text=question.question,
                output_path=question_path,
                duration=2.0,
                fontsize=12,
                max_width_px=600
            )

        video_files.append(question_path)
        video_files.append(answer_path)





    if not video_files:
        return f"Error: No video files found in {uploads_folder}."
    target_format = "webm"

 

    # converted_files = []
    # list_file_path = os.path.join(uploads_folder, "video_list.txt").replace("\\", "/")

    # output_filename = "merged_video.webm"


    # output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")
    # # FFMPEG_PATH = '/home/YOUR_CPANEL_USERNAME/ffmpeg/ffmpeg'
    # FFMPEG_PATH = 'C:/ffmpeg/bin/ffmpeg.exe'
    # # FFMPEG_PATH = '/usr/bin/ffmpeg'
    # logging.info("uploads_folder: %s", uploads_folder)
    # logging.info("output_filename: %s", output_filename)
    # logging.info("output_path check: %s", output_path)

    # for video in video_files:
    #     logging.info("video_list: %s", video)
    #     # input_path = os.path.join(uploads_folder, video).replace("\\", "/")
    #     input_path = video 
    #     logging.info("input_path: %s", input_path)
    #     output_path_converted = os.path.join(uploads_folder, f"{os.path.splitext(video)[0]}_converted.{target_format}").replace("\\", "/")
    #     logging.info("output_path_converted: %s", output_path_converted)
    #     # if not video.endswith(f".{target_format}"):
    #     #     # logging.info("target_format path video: %s", target_format)
    #     #     # convert_video(input_path, output_path_converted, target_format)
    #     #     # logging.info("ends with : %s", "end with")

    #     #     # converted_files.append(output_path_converted)
    #     #     # logging.info("target_format path video input_path output: %s", output_path_converted)
    #     #     ext = os.path.splitext(video)[1][1:].lower()
    #     #     if ext != target_format:
    #     #         # Make filename unique to avoid overwrite
    #     #         unique_id = uuid.uuid4().hex[:6]
    #     #         converted_name = f"{os.path.splitext(video)[0]}_{unique_id}_converted.{target_format}"
    #     #         converted_path = os.path.join(uploads_folder, converted_name).replace("\\", "/")
    #     #         logging.info("Converting: %s -> %s", input_path, converted_path)
    #     #         convert_video(input_path, converted_path, target_format)
    #     #         converted_files.append(converted_path)
    #     #     else:
    #     #         converted_files.append(input_path)

    #     # else:
    #     #     logging.info("target_format path video input_path: %s", input_path)

    #     #     converted_files.append(input_path)

    #             # Always normalize, regardless of extension
    #     try:
    #         video_codec, audio_codec = get_codecs(input_path)
    #         logging.info("Codecs - Video: %s, Audio: %s", video_codec, audio_codec)
    #     except Exception as e:
    #         logging.warning("Could not determine codecs. Forcing conversion. Error: %s", e)
    #         video_codec, audio_codec = None, None

    #     needs_conversion = True
    #     if (
    #             target_format == "webm" and
    #             video_codec == "vp8" and
    #             audio_codec == "opus" and
    #             is_video_valid(input_path)
    #         ):
    #             needs_conversion = False
    #     elif target_format == "mp4" and video_codec == "h264" and audio_codec in ["aac", "mp3"]:
    #         needs_conversion = False
    #     elif target_format == "mov" and video_codec == "prores":
    #         needs_conversion = False
        
    #     logging.info(f"Checking: {input_path} | Video Codec: {video_codec} | Audio Codec: {audio_codec}")

    #     if needs_conversion:
    #         unique_id = uuid.uuid4().hex[:6]
    #         converted_name = f"{os.path.splitext(video)[0]}_{unique_id}_converted.{target_format}"
    #         converted_path = os.path.join(uploads_folder, converted_name).replace("\\", "/")
    #         logging.info("Converting: %s -> %s", input_path, converted_path)
    #         convert_video(input_path, converted_path, target_format)
    #         converted_files.append(converted_path)
    #     else:
    #         logging.info("No conversion needed for: %s", input_path)
    #         converted_files.append(input_path)

    # with open(list_file_path, "w") as f:
    #     for video_path in converted_files:
    #         if os.path.exists(video_path):  # Only include if file exists
    #             f.write(f"file '{video_path}'\n")
    #         else:
    #             logging.warning("File does not exist, skipping in list: %s", video_path)


    # with open(list_file_path, "r") as debug_file:
    #     logging.info("video_list.txt contents:\n%s", debug_file.read())


    converted_files = []
    list_file_path = os.path.join(uploads_folder, "video_list.txt").replace("\\", "/")
    output_filename = "merged_video.webm"
    output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")

    # FFMPEG_PATH = '/home/YOUR_CPANEL_USERNAME/ffmpeg/ffmpeg'
    # FFMPEG_PATH = 'C:/ffmpeg/bin/ffmpeg.exe'
    # FFMPEG_PATH = '/usr/bin/ffmpeg'

    logging.info("uploads_folder: %s", uploads_folder)
    logging.info("output_filename: %s", output_filename)
    logging.info("output_path check: %s", output_path)

    for video in video_files:
        input_path = video
        logging.info("Processing video: %s", input_path)

        # ✅ 1. Skip missing or 0-byte files
        if not os.path.exists(input_path):
            logging.warning("Skipping missing file: %s", input_path)
            continue

        size = os.path.getsize(input_path)
        if size == 0:
            logging.warning("Skipping 0-byte file: %s", input_path)
            try:
                os.remove(input_path)  # optional cleanup
            except Exception as e:
                logging.warning("Failed to remove 0-byte file %s: %s", input_path, e)
            continue

        # ✅ 2. Check codecs to decide if conversion is required
        try:
            video_codec, audio_codec = get_codecs(input_path)
            logging.info("Codecs - Video: %s, Audio: %s", video_codec, audio_codec)
        except Exception as e:
            logging.warning("Could not determine codecs. Forcing conversion. Error: %s", e)
            video_codec, audio_codec = None, None

        needs_conversion = True
        if (
            target_format == "webm" and
            video_codec == "vp8" and
            audio_codec == "opus" and
            is_video_valid(input_path)
        ):
            needs_conversion = False
        elif target_format == "mp4" and video_codec == "h264" and audio_codec in ["aac", "mp3"]:
            needs_conversion = False
        elif target_format == "mov" and video_codec == "prores":
            needs_conversion = False

        # ✅ 3. Build deterministic converted file path (no UUIDs)
        converted_path = os.path.splitext(input_path)[0] + "_converted." + target_format

        if needs_conversion:
            if os.path.exists(converted_path) and os.path.getsize(converted_path) > 0:
                logging.info("Already converted, reusing: %s", converted_path)
            else:
                logging.info("Converting: %s -> %s", input_path, converted_path)
                try:
                    convert_video(input_path, converted_path, target_format)
                except subprocess.CalledProcessError as e:
                    logging.error("Conversion failed for %s: %s", input_path, e)
                    continue
            converted_files.append(converted_path)
        else:
            logging.info("No conversion needed for: %s", input_path)
            converted_files.append(input_path)

    # ✅ 4. Write only valid, non-empty files to list_file_path
    with open(list_file_path, "w") as f:
        for video_path in converted_files:
            if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                f.write(f"file '{video_path}'\n")
            else:
                logging.warning("Skipping empty/missing file in final list: %s", video_path)

    with open(list_file_path, "r") as debug_file:
        logging.info("video_list.txt contents:\n%s", debug_file.read())


    logging.info("target_format path target_format list: %s", target_format)
    logging.info("target_format path target_format list_file_path: %s", list_file_path)

    # if target_format == "webm":
    #     logging.info("enter it: %s", "webm")
    #     merge_command = f'ffmpeg -err_detect ignore_err -f concat -safe 0 -i "{list_file_path}" -c:v libvpx-vp9 -b:v 15M -c:a libopus "{output_path}"'
    #     logging.info("merge_command webm : %s", merge_command)
    # elif target_format == "mp4":
    #     merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -map 0:v -map 0:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
    # elif target_format == "mov":
    #     merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c:v prores -c:a pcm_s16le "{output_path}"'
    # else:
    #     logging.info("Unsupported format: %s", target_format)
    #     return f"Unsupported format: {target_format}"

    
    
    if target_format == "webm":
        merge_command = (
            f'{settings.FFMPEG_PATH} -f concat -safe 0 -i "{list_file_path}" '
            f'-c:v libvpx -b:v 1M -r 30 -pix_fmt yuv420p '
            f'-c:a libopus -ar 48000 -ac 2 '
            f'-f webm "{output_path}"'
        )

    elif target_format == "mp4":
        merge_command = (
            f'{settings.FFMPEG_PATH} -f concat -safe 0 -i "{list_file_path}" '
            f'-map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 28 '
            f'-vf scale=640:-2 -c:a aac -b:a 96k -movflags +faststart "{output_path}"'
        )
    elif target_format == "mov":
        merge_command = (
            f'{settings.FFMPEG_PATH} -f concat -safe 0 -i "{list_file_path}" '
            f'-c:v prores -c:a pcm_s16le "{output_path}"'
        )
    else:
        logging.info("Unsupported format: %s", target_format)
        return f"Unsupported format: {target_format}"

    try:
        logging.info("merge_command: %s", merge_command)
        subprocess.run(merge_command, shell=True, check=True)
        logging.info("merge_command subprocess: %s", merge_command)

        # transcript_file_path = transcribe_complete_video(output_path)

        # if transcript_file_path and os.path.exists(transcript_file_path):
        #     with open(transcript_file_path, "r", encoding="utf-8") as f:
        #         transcript_text = f.read()
        #         # Save to StudentInterviewLink
        #         try:
        #             interview_link.transcript_text = transcript_text
        #             interview_link.save(update_fields=["transcript_text"])
        #             logging.info("✅ Transcript text saved to StudentInterviewLink")
        #         except Exception as e:
        #             logging.warning("⚠️ Failed to save transcript to DB: %s", e)
        # else:
        #     logging.warning("Transcript generation failed or skipped.")

        # ✅ Transcribe full video and match segments to Q&A blocks
        import whisper
        model = whisper.load_model("small")

        # ✅ NEW CALL: Pass answers_qid_map to function
        qa_blocks = build_qa_blocks_with_paths(ordered_questions, answers_qid_map, uploads_folder)

        if not qa_blocks:
            logging.warning(f"⚠️  No valid Q&A pairs for transcription: {zoho_lead_id}")
            return "No valid Q&A pairs found."

        qa_transcript = []
        transcription_log = []

        # ❌ OLD: for idx, block in enumerate(qa_blocks, start=1):
        # ✅ NEW: Loop through blocks with question_id
        idx = 1  # ← manual counter
        for block in qa_blocks:
            question_id = block["question_id"]      # ← KEY: Use actual ID
            question_text = block["question_text"]
            answer_file = block["a_file"]
            
            try:
                logging.info(f"  📝 Transcribing Q.{question_id}...")
                result = model.transcribe(answer_file, language="en", word_timestamps=False)
                answer_text = result.get("text", "").strip()
                
                if not answer_text:
                    answer_text = "[No response detected]"
                
                # ✅ Use question_id, NOT enumerate index
                # qa_transcript.append(f"Q.{question_id}: {question_text}\nANS: {answer_text}\n")
                #                        ↑ CORRECT: Actual question_id from database

                qa_transcript.append(f"Q.{idx}: {question_text}\nANS: {answer_text}\n")
                idx += 1  # Increment manual counter
                
                transcription_log.append({
                    "question_id": question_id,
                    "status": "success"
                })
                
                logging.info(f"  ✅ Q.{question_id} transcribed")
                
            except Exception as e:
                logging.error(f"  ❌ Transcription failed for Q.{question_id}: {str(e)}")
                transcription_log.append({
                    "question_id": question_id,
                    "status": "failed",
                    "error": str(e)
                })

        transcript_output = "\n".join(qa_transcript)
        transcript_txt_path = os.path.splitext(output_path)[0] + "_transcript.txt"
        with open(transcript_txt_path, "w", encoding="utf-8") as f:
            f.write(transcript_output)

        # Save to DB
        interview_link.transcript_text = transcript_output
        interview_link.save(update_fields=["transcript_text"])
        clean_transcript = transcript_output.strip()
        clean_transcript = re.sub(r'^[ \t]+(Q\.\d+:)', r'\1', clean_transcript, flags=re.MULTILINE)
        formatted_transcript = escape(clean_transcript).replace("\n", "<br>")

        # ✅ Save Q&A transcript to file and DB
        # transcript_output = "\n".join(qa_transcript)
        # transcript_txt_path = os.path.splitext(output_path)[0] + "_transcript.txt"

        # with open(transcript_txt_path, "w", encoding="utf-8") as f:
        #     f.write(transcript_output)

        # try:
        #     interview_link.transcript_text = transcript_output
        #     interview_link.save(update_fields=["transcript_text"])
        #     logging.info("✅ Formatted transcript saved to DB and file.")
        # except Exception as e:
        #     logging.warning("⚠️ Failed to save formatted transcript to DB: %s", e)

        video_id = upload_to_bunnystream(output_path)
        logging.info("video_id: %s", video_id)
        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        student.bunny_stream_video_id = video_id
        student.save()

        # Email configuration
        # video_path = os.path.join(
        #     "/home/ascenciaintervie/public_html/uploads/interview_videos",
        #     zoho_lead_id,
        #     "merged_video.webm"
        # )



        video_path = os.path.join(
            # "/home/ascenciaintervie/public_html/static/uploads/interview_videos",
            # "/home/interview/public_html/static/uploads/interview_videos",
            # "C:/xampp/htdocs/vaibhav/ascencia_interviews/static/uploads/interview_videos",
            settings.UPLOADS_FOLDER,
            zoho_lead_id,
            "merged_video.webm"
        )

        # Email configuration
        

        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        student_name = f"{student.first_name} {student.last_name}"
        student_email = student.email
        student_zoho_lead_id = student.zoho_lead_id
        student_program = student.program 

        email = student.student_manager_email.strip().lower()
        student_manager = User.objects.filter(email__iexact=email).first()
        student_manager_name = ''
        if student_manager:  
            student_manager_name = f"{student_manager.first_name} {student_manager.last_name}".strip()
            print(f"student_manager_name: {student_manager_name}")
            student_manager_email= student_manager.email


        student1 = Students.objects.get(zoho_lead_id=zoho_lead_id)
        crm_id = student1.crm_id
        logo_url, company_name = get_email_branding(crm_id)

        subject = "Interview Process Completed"
        recipient = [student_manager_email]
        from_email = ''
        # url = video_path  # or your public URL if available
        url = f"https://video.bunnycdn.com/play/{settings.BUNNY_STREAM_LIBRARY_ID}/{video_id}"

        html_content = f"""
        <html>
            <body style="background-color: #f4f4f4; font-family: Tahoma, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh;">
                <div class="email-container" style="background: #ffffff; max-width: 600px; width: 100%; padding: 30px 25px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); border: 1px solid #ddd; box-sizing: border-box;margin:0 auto">
                    
                    <!-- Logo Header -->
                    <div class="header" style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee;">
                    <img src="{logo_url}" alt="Company Logo" style="height: 70px; width: auto; margin-bottom: 10px;">
                    </div>

                    <!-- Illustration -->
                    <img src="https://ascencia-interview.com/static/img/email_template_icon/interviewcomplete.png" alt="Document Verified" style="width: 50%; display: block; margin: 20px auto;" />

                    <!-- Heading -->
                    <h2 style="color: #2c3e50; text-align: center;">Interview Process Submitted</h2>

                    <!-- Content -->
                    <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Dear <b>{student_manager_name}</b>,</p>

                    <!-- <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">The interview process has been successfully completed.</p> -->
                    <!-- <p style="color: #555; font-size: 16px; line-h eight: 1.6; text-align: left;">The interview video is attached. Please review.</p> -->
                    
                    <!-- Content -->
                    <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;"><b>Student Details:</b></p>
                    <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Name: {student_name},</p>
                    <p style="color: #555; font-size: 14px; text-align: left;">Email: {student_email}</p>
                    <p style="color: #555; font-size: 14px; text-align: left;">Zoho Lead Id: {student_zoho_lead_id}</p>
                    <p style="color: #555; font-size: 14px; text-align: left;">Student Program: {student_program}</p>


                    <!--change for link -->
                    <!-- Watch Video Button -->
                    <div style="text-align: left; margin-top: 30px;">
                        <a href="{url}" target="_blank" style="background-color: #007bff; color: white; padding: 12px 25px; font-size: 16px; text-decoration: none; border-radius: 5px;">Watch Video</a>
                    </div>

                    <!-- Transcript Section -->
                    <h3 style="color: #2c3e50; margin-top: 40px;">Interview Transcript</h3>
                    <div style="background: #f9f9f9; border: 1px solid #ddd; padding: 15px; border-radius: 5px; font-size: 14px; line-height: 1.5; color: #333;">
                        {formatted_transcript}
                    </div>

                    <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left; margin-top: 30px;">
                                                    Best regards,<br/>{company_name}
                                                </p>
                </div>
                
            </body>
        </html>
        """
        # Create the email object
        email = EmailMultiAlternatives(
            subject=subject,
            body="Interview process complete. Please view the attached video or click the button.",
            from_email=from_email,
            to=recipient,
        )
        # 🔥 Add this to auto-apply CC everywhere
        email.cc = settings.DEFAULT_CC_EMAILS
        print(r"cc",settings.DEFAULT_CC_EMAILS)
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        print(r"html_content",html_content)

        # Check and attach the video
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            if file_size < 10 * 1024 * 1024:  # < 25MB
                print(r"filesize",file_size)
                with open(video_path, "rb") as f:
                    mime_type, _ = mimetypes.guess_type(video_path)
                    email.attach("interview_video.webm", f.read(), mime_type or "application/octet-stream")
                    print(r"Mime Type",mime_type)

                    logging.info("Video attached successfully.")
            else:
                print(r"dfsf","check video")
                logging.warning("Video is too large to attach. Send only the link.")
        else:
            print(r"dfsf","file not found")
            logging.error(f"File not found: {video_path}")

        # Send email
        email.send()

        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        student.bunny_stream_video_id = video_id
        student.save()
        # add for completed interview process with send mail link
        try:
            for file in os.listdir(uploads_folder):
                file_path = os.path.join(uploads_folder, file)
                if os.path.isfile(file_path) and file_path.endswith((".webm", ".mp4", ".mov", ".txt")):
                    os.remove(file_path)
            logging.info("All video and temp files deleted from uploads folder: %s", uploads_folder)
        except Exception as cleanup_error:
            logging.warning("Failed to clean up uploads folder: %s", cleanup_error)

         # Delete StudentInterviewAnswers after processing
        deleted_count, _ = StudentInterviewAnswers.objects.filter(zoho_lead_id=zoho_lead_id).delete()
        delted_student_interview = StudentInterview.objects.filter(zoho_lead_id=zoho_lead_id).update(interview_process='')
        
        # ✅ Send "Thank You" Email to Student
        send_email(
            subject="Thank You for Completing Your Interview!",
            message=f"""
            <html>
                <head>
                    <style>
                        body {{
                            background-color: #f4f4f4;
                            font-family: Tahoma, sans-serif;
                            margin: 0;
                            padding: 40px 20px;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                        }}
                        .email-container {{
                            background: #ffffff;
                            max-width: 600px;
                            width: 100%;
                            padding: 30px 25px;
                            border-radius: 10px;
                            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
                            border: 1px solid #ddd;
                            box-sizing: border-box;
                            margin: 0 auto;
                        }}
                        .header {{
                            text-align: center;
                            margin-bottom: 20px;
                            border-bottom: 1px solid #eee;
                        }}
                        .header img {{
                            height: 70px;
                            width: auto;
                            margin-bottom: 10px;
                        }}
                        .email-logo {{
                            width: 50%;
                            display: block;
                            margin: 20px auto;
                        }}
                        h2 {{
                            color: #2c3e50;
                            text-align: center;
                        }}
                        p {{
                            color: #555;
                            font-size: 16px;
                            line-height: 1.6;
                            text-align: left;
                        }}
                        @media only screen and (max-width: 600px) {{
                            .email-logo {{
                                width: 80% !important;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="header">
                            <img src="{logo_url}" alt="Ascencia Malta" />
                        </div>
                        <img src="https://ascencia-interview.com/static/img/email_template_icon/Thank_you-01.png" alt="Interview Completed" class="email-logo" />
                        
                        <h2>Thank You for Completing Your Interview!</h2>

                        <p>Hi <b>{student_name.split()[0]}</b>,</p>

                        <p>Thank you for taking the time to complete your interview. We appreciate your effort and enthusiasm!</p>

                        <p>Your Student Manager will be reviewing your interview details and will get back to you shortly with the next steps. If you have any questions in the meantime, feel free to reply to this email.</p>

                        <p>We’re excited to support you on your journey!</p>

                        <p>Best regards,<br/>
                        {company_name}</p>
                    </div>
                </body>
            </html>
            """,
            
            recipient=[student_email],
            reply_to=[student_manager_email]
        )
        logging.info("Deleted %s StudentInterviewAnswers entries for zoho_lead_id: %s", deleted_count, zoho_lead_id)


        return f"video_id: Done"

    except subprocess.CalledProcessError as e:
        logging.info("error subprocess: %s", "test error")
        return f"Error merging videos: {e}"


@receiver(post_save, sender=StudentInterviewAnswers)
def handle_student_interview_answer_save(sender, instance, created, **kwargs):
    logger.info("post_save fired for %s created=%s", instance.zoho_lead_id, created)
    if not created:
        return

    zoho_lead_id = instance.zoho_lead_id
    

     # Fetch interview_link_count from DB
    try:
        interview_link_obj = StudentInterviewLink.objects.get(zoho_lead_id=zoho_lead_id)
        interview_link_count = interview_link_obj.interview_link_count
    except StudentInterviewLink.DoesNotExist:
        logger.warning("No StudentInterviewLink found for zoho_lead_id=%s", zoho_lead_id)
        interview_link_count = None

    # Optional: only schedule when at least 1 answer exists (or change to == 6 if you need exactly 6)
    # answers_count = sender.objects.filter(zoho_lead_id=zoho_lead_id).count()
    # if answers_count < 1:
    #     logger.info("Not enough answers for lead %s yet. Skipping scheduling.", zoho_lead_id)
    #     return

    # ALWAYS compute from now(), not created_at
    run_time = now() + timedelta(minutes=30)

    # De-duplicate: ensure only ONE pending schedule per lead
    schedule_name = f"merge_videos:{zoho_lead_id}"
    Schedule.objects.filter(name=schedule_name).delete()

    print("helloo")
    schedule(
        "studentpanel.observer.video_merge_handler.merge_videos",  # dotted path
        zoho_lead_id,                    # positional arg to the task
        interview_link_count=interview_link_count,  # ✅ keyword argument  # pass as keyword argument
        schedule_type="O",                # One-time
        next_run=run_time,                # exact run time
        name=schedule_name,               # lets us de-duplicate
    )

    logger.info("Scheduled merge_videos for lead=%s at %s", zoho_lead_id, run_time)

# @receiver(post_save, sender=StudentInterviewAnswers)
# def handle_student_interview_answer_save(sender, instance, created, **kwargs):
#     if created:
#         # Run your custom logic here when a new StudentInterviewAnswer is created
#         print(f'New answer created: {instance}')
#         zoho_lead_id = instance.zoho_lead_id
#         last_6_answers = sender.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-created_at')[:6]
#         print(r'last_6_answers_count:', last_6_answers)
#         # Schedule merge 10 minutes after created_at
#         run_time = instance.created_at + timedelta(minutes=10)
#         schedule(
#             "studentpanel.observer.video_merge_handler.merge_videos",
#             zoho_lead_id,
#             schedule_type="O",  # One-time task
#             next_run=run_time
#         )

#         print(f"Scheduled merge for Zoho Lead {zoho_lead_id} at {run_time}")
    #     if last_6_answers.count() == 6:
    #         time.sleep(10)
    #         print(r'last_6_answers_count text:', last_6_answers.count())
    #         async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)
    #         # async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)
    #         # async_task(merge_videos, zoho_lead_id)
    # else:
    #     # Handle updates to existing answers
    #     print(f'Answer updated: {instance}')
    # logging.info("Created: %s", "Created")
    # if created:
    #     # logging.info("Observer Triggered: %s", "triggered")
    #     # last_question_id = instance.last_question_id
    #     # logging.info("Last Question ID: %s", last_question_id)
    #     # question_id = instance.question_id
    #     # logging.info("Question ID: %s", question_id)
    #     zoho_lead_id = instance.zoho_lead_id
    #     logging.info("Zoho Lead ID: %s", zoho_lead_id)

    #     # if int(last_question_id) == int(question_id):
    #         # print(r'last_question_id:', last_question_id)
    #     last_5_answers = sender.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-created_at')[:5]
    #     print(r'last_5_answers_count:', last_5_answers)
    #     # if last_5_answers.count() == 5:
    #     async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)




# add celery code 


# @receiver(post_save, sender=StudentInterviewAnswers)
# def handle_student_interview_answer_save(sender, instance, created, **kwargs):
#     if created:
#         print(f'New answer created: {instance}')
#         zoho_lead_id = instance.zoho_lead_id
#         last_5_answers = sender.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-created_at')[:5]
#         if last_5_answers.count() == 5:
#             print(f'[SIGNAL] Triggering Celery merge task for: {zoho_lead_id}')
#             merge_videos_task.delay(str(zoho_lead_id))  # Ensure it's serializable
#     else:
#         print(f'Answer updated: {instance}')
