import os
import subprocess
import requests
from django.conf import settings
from studentpanel.models.interview_process_model import Students
from adminpanel.utils import send_email
from django.db.models.signals import post_save
from django.dispatch import receiver
from studentpanel.models.student_interview_answer import StudentInterviewAnswers
from django_q.tasks import async_task
import logging

logging.basicConfig(level=logging.INFO)
def get_uploads_folder():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    logging.info("project_root: %s", project_root)
    uploads_folder = os.path.join(project_root, "uploads", "interview_videos")
    logging.info("uploads folder text: %s", uploads_folder)
    return uploads_folder.replace("\\", "/")


def convert_video(input_path, output_path, target_format):
    logging.info("output_path: %s", output_path)
    logging.info("target_format path: %s", target_format)
    if target_format == "webm":
        command = f'ffmpeg -i "{input_path}" -c:v libvpx-vp9 -b:v 1M -c:a libopus "{output_path}"'
    elif target_format == "mp4":
        command = f'ffmpeg -i "{input_path}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
    elif target_format == "mov":
        command = f'ffmpeg -i "{input_path}" -c:v prores -c:a pcm_s16le "{output_path}"'
    else:
        raise ValueError(f"Unsupported format: {target_format}")

    subprocess.run(command, shell=True, check=True)


def upload_to_bunnystream(video_path):
    video_name = os.path.basename(video_path)

    create_url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos"
    headers = {
        "AccessKey": settings.BUNNY_STREAM_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(create_url, json={"title": video_name}, headers=headers)
    video_id = response.json().get("guid")
    if not video_id:
        return "Error: Video GUID not received."

    upload_url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos/{video_id}"
    headers = {
        "AccessKey": settings.BUNNY_STREAM_API_KEY,
        "Content-Type": "application/octet-stream"
    }

    with open(video_path, "rb") as video_file:
        upload_response = requests.put(upload_url, headers=headers, data=video_file)

    if upload_response.status_code != 201:
        return f"Error uploading video: {upload_response.text}"

    return video_id


def merge_videos(zoho_lead_id):
    uploads_folder = os.path.join(get_uploads_folder(), zoho_lead_id)
    logging.info("uploads_folder: %s", uploads_folder)

    if not os.path.exists(uploads_folder):
        return f"Error: Folder {uploads_folder} does not exist."

    video_files = [f for f in os.listdir(uploads_folder) if f.endswith((".webm", ".mp4", ".mov"))]
    if not video_files:
        return f"Error: No video files found in {uploads_folder}."

    first_video_ext = os.path.splitext(video_files[0])[1][1:].lower()
    logging.info("first_video_ext: %s", first_video_ext)
    target_format = first_video_ext
    logging.info("target_format: %s", target_format)

    converted_files = []
    list_file_path = os.path.join(uploads_folder, "video_list.txt").replace("\\", "/")
    output_filename = f"merged_video.{target_format}"
    output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")
    logging.info("uploads_folder: %s", uploads_folder)
    logging.info("output_filename: %s", output_filename)
    logging.info("output_path check: %s", output_path)

    for video in video_files:
        logging.info("video_list: %s", video)
        input_path = os.path.join(uploads_folder, video).replace("\\", "/")
        logging.info("input_path: %s", input_path)
        output_path_converted = os.path.join(uploads_folder, f"{os.path.splitext(video)[0]}_converted.{target_format}").replace("\\", "/")
        logging.info("output_path_converted: %s", output_path_converted)
        if not video.endswith(f".{target_format}"):
            logging.info("target_format path video: %s", target_format)
            convert_video(input_path, output_path_converted, target_format)
            logging.info("ends with : %s", "end with")

            converted_files.append(output_path_converted)
            logging.info("target_format path video input_path output: %s", output_path_converted)

        else:
            logging.info("target_format path video input_path: %s", input_path)

            converted_files.append(input_path)

    with open(list_file_path, "w") as f:
        for video in converted_files:
            f.write(f"file '{video}'\n")
            logging.info("target_format path video list: %s", video)

    logging.info("target_format path target_format list: %s", target_format)
    logging.info("target_format path target_format list_file_path: %s", list_file_path)

    if target_format == "webm":
        logging.info("enter it: %s", "webm")
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c:v libvpx-vp9 -b:v 1M -c:a libopus "{output_path}"'
        logging.info("merge_command webm : %s", merge_command)
    elif target_format == "mp4":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -map 0:v -map 0:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
    elif target_format == "mov":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c:v prores -c:a pcm_s16le "{output_path}"'
    else:
        logging.info("Unsupported format: %s", target_format)
        return f"Unsupported format: {target_format}"

    try:
        logging.info("merge_command: %s", merge_command)
        
        subprocess.run(merge_command, shell=True, check=True)

        video_id = upload_to_bunnystream(output_path)
        logging.info("video_id: %s", video_id)
        # student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        # student.bunny_stream_video_id = video_id
        # student.save()

        url = f"{settings.ADMIN_BASE_URL}/uploads/interview_videos/{zoho_lead_id}/merge_videos.webm"

        send_email(
            subject="Interview Process Completed",
            message=f"""
                    <html>
                    <body>
                         <table role="presentation" cellspacing="0" cellpadding="0" width="100%">
                            <tr>
                                <td align="center">
                                    <div class="email-container">
                                        <!-- Logo Header -->
                                        <div class="header">
                                            <img src="One.png" alt="Company Logo">
                                        </div>
                                         <img src="{{ STATIC_URL }}img/email_template_icon/doc_verified.png" alt="Document Verified" class="email-logo"/>
                                        <!-- Main Content -->
                                        <h2>Interview Process Completed</h2>
                                        <p>Dear User,</p>
                                        <p>The interview process has been successfully completed.</p>
                                        <p>Please review the interview video using the button below:</p>
                                        <!-- CTA Button -->
                                        <div class="btn-container">
                                            <a href="{ url }" class="btn">Check Interview Video</a>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        </table>
                        
                    </body>
                    </html>
                """,
            recipient=["ankita@angel-portal.com"],
            # cc=["admin@example.com", "hr@example.com"]  # CC recipients
        )

        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        student.bunny_stream_video_id = video_id
        student.save()
        return f"video_id: {video_id}"

    except subprocess.CalledProcessError as e:
        return f"Error merging videos: {e}"


@receiver(post_save, sender=StudentInterviewAnswers)
def handle_student_interview_answer_save(sender, instance, created, **kwargs):
    logging.info("Created: %s", "Created")
    if created:
        logging.info("Observer Triggered: %s", "triggered")
        last_question_id = instance.last_question_id
        logging.info("Last Question ID: %s", last_question_id)
        question_id = instance.question_id
        logging.info("Question ID: %s", question_id)
        zoho_lead_id = instance.zoho_lead_id
        logging.info("Zoho Lead ID: %s", zoho_lead_id)

        if int(last_question_id) == int(question_id):
            print(r'last_question_id:', last_question_id)
            last_5_answers = sender.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-created_at')[:5]
            print(r'last_5_answers_count:', last_5_answers)
            if last_5_answers.count() == 5:
                async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)