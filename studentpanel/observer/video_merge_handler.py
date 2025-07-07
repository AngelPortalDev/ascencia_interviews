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
from studentpanel.models.student_Interview_status import Student_Interview
from studentpanel.models.interview_link import StudentInterviewLink
import time
from adminpanel.models.common_question import CommonQuestion
logging.basicConfig(level=logging.INFO)
import uuid
import json
import whisper
import warnings

def get_uploads_folder():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    logging.info("project_root: %s", project_root)
    uploads_folder = os.path.join(project_root,"static","uploads", "interview_videos")
    logging.info("uploads folder text: %s", uploads_folder)
    return uploads_folder.replace("\\", "/")


def convert_video(input_path, output_path, target_format):
    # FFMPEG_PATH = 'C:/ffmpeg/bin/ffmpeg.exe'
    FFMPEG_PATH = '/usr/bin/ffmpeg'
    logging.info("output_path: %s", output_path)
    logging.info("target_format path: %s", target_format)
    if target_format == "webm":
        command = (
            f'{FFMPEG_PATH} -y -i "{input_path}" '
            f'-vf scale=640:480 -r 30 -pix_fmt yuv420p '
            f'-c:v libvpx -b:v 1M -quality good -cpu-used 4 '
            f'-qmin 10 -qmax 42 '
            f'-c:a libopus -application voip -b:a 96k -vbr on '
            f'-movflags faststart -avoid_negative_ts make_zero '
            f'"{output_path}"'
        )


    elif target_format == "mp4":
        command = f'ffmpeg -i "{input_path}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
    elif target_format == "mov":
        command = f'ffmpeg -i "{input_path}" -c:v prores -c:a pcm_s16le "{output_path}"'
    else:
        raise ValueError(f"Unsupported format: {target_format}")

    subprocess.run(command, shell=True, check=True)

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

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
    FFMPEG_PROBE = '/usr/bin/ffprobe'
    # FFMPEG_PROBE = "C:/ffmpeg/bin/ffprobe.exe"
    cmd = [
        FFMPEG_PROBE, "-v", "error",
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

    
    
def generate_question_video(text, output_path, duration=2):
    # FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # raw string avoids escaping
    FFMPEG_PATH = '/usr/bin/ffmpeg'
    # font_path = "C\\\\:/Windows/Fonts/arial.ttf"
    font_path = "/usr/share/fonts/dejavu/DejaVuSans.ttf"


      # ✅ Escape special characters properly for FFmpeg
    #   this only one line Questions
    # safe_text = text.replace(":", r'\:').replace("?", r'\?').replace("'", "").replace('"', "")
    # for new line like two line questions 
    safe_text = text.replace("\n", " ").replace(":", r'\:').replace("?", r'\?').replace("'", "").replace('"', "")

    drawtext = (
    f"drawtext=fontfile={font_path}:"
    f"text='{safe_text}':fontcolor=white:fontsize=12:x=(w-text_w)/2:y=(h-text_h)/2"
    )
    print("drawtext",drawtext)

    command = (
        f'"{FFMPEG_PATH}" '
        f'-f lavfi -i color=c=black:s=640x360:d={duration} '
        f'-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 '
        f'-shortest -vf "{drawtext}" '
        f'-c:v libvpx -b:v 1M -c:a libopus -ar 48000 -ac 2 '
        f'-f webm -y "{output_path}"'
    )


    logging.info("Running FFmpeg command:\n%s", command)

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error("FFmpeg failed to generate VP8+Opus question video: %s", e)
        raise


    
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
    FFMPEG_PROBE = '/usr/bin/ffprobe'

    cmd_video = [
        FFMPEG_PROBE, '-v', 'error',
        '-select_streams', 'v:0', '-show_entries', 'stream=codec_name',
        '-of', 'json', video_path
    ]
    result_video = subprocess.run(cmd_video, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    video_codec = json.loads(result_video.stdout)["streams"][0]["codec_name"].lower()

    cmd_audio = [
        FFMPEG_PROBE, '-v', 'error',
        '-select_streams', 'a:0', '-show_entries', 'stream=codec_name',
        '-of', 'json', video_path
    ]
    result_audio = subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    audio_codec = json.loads(result_audio.stdout)["streams"][0]["codec_name"].lower()

    return video_codec, audio_codec


def is_video_valid(video_path):
    # FFMPEG_PROBE = 'C:/ffmpeg/bin/ffprobe.exe'
    FFMPEG_PROBE = '/usr/bin/ffprobe'
    try:
        cmd = [
            FFMPEG_PROBE, "-v", "error",
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


def merge_videos(zoho_lead_id,interview_link_count=None):
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

    if not interview_link.assigned_question_ids:
        return f"No assigned questions for zoho_lead_id: {zoho_lead_id}"

    question_id_list = list(map(int, interview_link.assigned_question_ids.split(",")))

    # ✅ Fetch answer objects in order of submission
    answers = list(StudentInterviewAnswers.objects.filter(
        zoho_lead_id=zoho_lead_id
    ).order_by("created_at")[:len(question_id_list)])

    if not answers:
        return f"No answers found for lead ID {zoho_lead_id}."

    # ✅ Fetch questions by ID and preserve order from interview_link
    questions_qs = CommonQuestion.active_objects.filter(id__in=question_id_list)
    question_map = {q.id: q for q in questions_qs}
    ordered_questions = [question_map[qid] for qid in question_id_list if qid in question_map]

    if len(ordered_questions) < len(answers):
        return f"Some question IDs are missing from CommonQuestion."

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    video_files = []

    # 🔁 Pair each question with its corresponding answer
    for i, (answer, question) in enumerate(zip(answers, ordered_questions), start=1):
        question_filename = f"question_{question.id}.webm"
        question_path = os.path.join(uploads_folder, question_filename).replace("\\", "/")
        answer_path = os.path.join(project_root, answer.video_path).replace("\\", "/")

        if not os.path.exists(answer_path):
            return f"Missing answer file: {answer_path}"

        if not os.path.exists(question_path):
            generate_question_video(f"{question.question}", question_path, duration=2.0)

        video_files.append(question_path)
        video_files.append(answer_path)




    if not video_files:
        return f"Error: No video files found in {uploads_folder}."
    target_format = "webm"


    converted_files = []
    list_file_path = os.path.join(uploads_folder, "video_list.txt").replace("\\", "/")

    output_filename = "merged_video.webm"


    output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")
    # FFMPEG_PATH = '/home/YOUR_CPANEL_USERNAME/ffmpeg/ffmpeg'
    # FFMPEG_PATH = 'C:/ffmpeg/bin/ffmpeg.exe'
    FFMPEG_PATH = '/usr/bin/ffmpeg'
    logging.info("uploads_folder: %s", uploads_folder)
    logging.info("output_filename: %s", output_filename)
    logging.info("output_path check: %s", output_path)

    for video in video_files:
        logging.info("video_list: %s", video)
        # input_path = os.path.join(uploads_folder, video).replace("\\", "/")
        input_path = video 
        logging.info("input_path: %s", input_path)
        output_path_converted = os.path.join(uploads_folder, f"{os.path.splitext(video)[0]}_converted.{target_format}").replace("\\", "/")
        logging.info("output_path_converted: %s", output_path_converted)
        # if not video.endswith(f".{target_format}"):
        #     # logging.info("target_format path video: %s", target_format)
        #     # convert_video(input_path, output_path_converted, target_format)
        #     # logging.info("ends with : %s", "end with")

        #     # converted_files.append(output_path_converted)
        #     # logging.info("target_format path video input_path output: %s", output_path_converted)
        #     ext = os.path.splitext(video)[1][1:].lower()
        #     if ext != target_format:
        #         # Make filename unique to avoid overwrite
        #         unique_id = uuid.uuid4().hex[:6]
        #         converted_name = f"{os.path.splitext(video)[0]}_{unique_id}_converted.{target_format}"
        #         converted_path = os.path.join(uploads_folder, converted_name).replace("\\", "/")
        #         logging.info("Converting: %s -> %s", input_path, converted_path)
        #         convert_video(input_path, converted_path, target_format)
        #         converted_files.append(converted_path)
        #     else:
        #         converted_files.append(input_path)

        # else:
        #     logging.info("target_format path video input_path: %s", input_path)

        #     converted_files.append(input_path)

                # Always normalize, regardless of extension
        try:
            video_codec, audio_codec = get_codecs(input_path)
            logging.info("Codecs - Video: %s, Audio: %s", video_codec, audio_codec)
        except Exception as e:
            logging.warning("Could not read codecs, force conversion: %s", e)
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
        
        logging.info(f"Checking: {input_path} | Video Codec: {video_codec} | Audio Codec: {audio_codec}")

        if needs_conversion:
            unique_id = uuid.uuid4().hex[:6]
            converted_name = f"{os.path.splitext(video)[0]}_{unique_id}_converted.{target_format}"
            converted_path = os.path.join(uploads_folder, converted_name).replace("\\", "/")
            logging.info("Converting: %s -> %s", input_path, converted_path)
            convert_video(input_path, converted_path, target_format)
            converted_files.append(converted_path)
        else:
            logging.info("No conversion needed for: %s", input_path)
            converted_files.append(input_path)

    with open(list_file_path, "w") as f:
        for video_path in converted_files:
            if os.path.exists(video_path):  # Only include if file exists
                f.write(f"file '{video_path}'\n")
            else:
                logging.warning("File does not exist, skipping in list: %s", video_path)


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
        f'{FFMPEG_PATH} -f concat -safe 0 -i "{list_file_path}" '
        f'-c:v libvpx -b:v 1M -r 30 -pix_fmt yuv420p '
        f'-c:a libopus -ar 48000 -ac 2 '
        f'-movflags faststart -avoid_negative_ts make_zero '
        f'"{output_path}"'
    )

    elif target_format == "mp4":
        merge_command = (
            f'{FFMPEG_PATH} -f concat -safe 0 -i "{list_file_path}" '
            f'-map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 28 '
            f'-vf scale=640:-2 -c:a aac -b:a 96k -movflags +faststart "{output_path}"'
        )
    elif target_format == "mov":
        merge_command = (
            f'{FFMPEG_PATH} -f concat -safe 0 -i "{list_file_path}" '
            f'-c:v prores -c:a pcm_s16le "{output_path}"'
        )
    else:
        logging.info("Unsupported format: %s", target_format)
        return f"Unsupported format: {target_format}"

    try:
        logging.info("merge_command: %s", merge_command)
        subprocess.run(merge_command, shell=True, check=True)
        logging.info("merge_command subprocess: %s", merge_command)

        transcript_file_path = transcribe_complete_video(output_path)

        if transcript_file_path and os.path.exists(transcript_file_path):
            with open(transcript_file_path, "r", encoding="utf-8") as f:
                transcript_text = f.read()
                # Save to StudentInterviewLink
                try:
                    interview_link.transcript_text = transcript_text
                    interview_link.save(update_fields=["transcript_text"])
                    logging.info("✅ Transcript text saved to StudentInterviewLink")
                except Exception as e:
                    logging.warning("⚠️ Failed to save transcript to DB: %s", e)
        else:
            logging.warning("Transcript generation failed or skipped.")

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
            "/home/ascenciaintervie/public_html/static/uploads/interview_videos",
            # "C:/xampp/htdocs/vaibhav/ascencia_interviews/static/uploads/interview_videos",
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
                    <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Company Logo" style="height: 40px; width: auto; margin-bottom: 10px;">
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
                    <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left; margin-top: 30px;">
                                                    Best regards,<br/>Ascencia Malta
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

        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        print(r"html_content",html_content)

        # Check and attach the video
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            if file_size < 25 * 1024 * 1024:  # < 25MB
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
        delted_student_interview = Student_Interview.objects.filter(zoho_lead_id=zoho_lead_id).update(interview_process='')

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
                            height: 40px;
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
                            <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Ascencia Malta" />
                        </div>
                        <img src="https://ascencia-interview.com/static/img/email_template_icon/Thank_you-01.png" alt="Interview Completed" class="email-logo" />
                        
                        <h2>Thank You for Completing Your Interview!</h2>

                        <p>Hi <b>{student_name.split()[0]}</b>,</p>

                        <p>Thank you for taking the time to complete your interview. We appreciate your effort and enthusiasm!</p>

                        <p>Your Student Manager will be reviewing your interview details and will get back to you shortly with the next steps. If you have any questions in the meantime, feel free to reply to this email.</p>

                        <p>We’re excited to support you on your journey!</p>

                        <p>Best regards,<br/>
                        Ascencia Malta</p>
                    </div>
                </body>
            </html>
            """,
            recipient=[student_email]
        )
        logging.info("Deleted %s StudentInterviewAnswers entries for zoho_lead_id: %s", deleted_count, zoho_lead_id)


        return f"video_id: Done"

    except subprocess.CalledProcessError as e:
        logging.info("error subprocess: %s", "test error")
        return f"Error merging videos: {e}"


@receiver(post_save, sender=StudentInterviewAnswers)
def handle_student_interview_answer_save(sender, instance, created, **kwargs):
    if created:
        # Run your custom logic here when a new StudentInterviewAnswer is created
        print(f'New answer created: {instance}')
        zoho_lead_id = instance.zoho_lead_id
        last_6_answers = sender.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-created_at')[:6]
        print(r'last_6_answers_count:', last_6_answers)
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
