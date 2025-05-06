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


def get_uploads_folder():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    uploads_folder = os.path.join(project_root, "uploads", "interview_videos")
    return uploads_folder.replace("\\", "/")


def convert_video(input_path, output_path, target_format):
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

    if not os.path.exists(uploads_folder):
        return f"Error: Folder {uploads_folder} does not exist."

    video_files = [f for f in os.listdir(uploads_folder) if f.endswith((".webm", ".mp4", ".mov"))]
    if not video_files:
        return f"Error: No video files found in {uploads_folder}."

    first_video_ext = os.path.splitext(video_files[0])[1][1:].lower()
    target_format = first_video_ext

    converted_files = []
    list_file_path = os.path.join(uploads_folder, "video_list.txt").replace("\\", "/")
    output_filename = f"merged_video.{target_format}"
    output_path = os.path.join(uploads_folder, output_filename).replace("\\", "/")

    for video in video_files:
        input_path = os.path.join(uploads_folder, video).replace("\\", "/")
        output_path_converted = os.path.join(uploads_folder, f"{os.path.splitext(video)[0]}_converted.{target_format}").replace("\\", "/")

        if not video.endswith(f".{target_format}"):
            convert_video(input_path, output_path_converted, target_format)
            converted_files.append(output_path_converted)
        else:
            converted_files.append(input_path)

    with open(list_file_path, "w") as f:
        for video in converted_files:
            f.write(f"file '{video}'\n")

    if target_format == "webm":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c:v libvpx-vp9 -b:v 1M -c:a libopus "{output_path}"'
    elif target_format == "mp4":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -map 0:v -map 0:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "{output_path}"'
    elif target_format == "mov":
        merge_command = f'ffmpeg -f concat -safe 0 -i "{list_file_path}" -c:v prores -c:a pcm_s16le "{output_path}"'
    else:
        return f"Unsupported format: {target_format}"

    try:
        subprocess.run(merge_command, shell=True, check=True)

        video_id = upload_to_bunnystream(output_path)
        print(video_id)
        # student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        # student.bunny_stream_video_id = video_id
        # student.save()

        url = f"{settings.ADMIN_BASE_URL}/uploads/interview_videos/{zoho_lead_id}/merge_videos.webm"
        video_path = f"/home/ascenciaintervie/public_html/uploads/interview_videos/{zoho_lead_id}/merge_videos.webm"

        send_email(
            subject="Interview Process Completed",
            message=f"""
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
                            <h2 style="color: #2c3e50; text-align: center;">Interview Process Completed</h2>

                            <!-- Content -->
                            <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: center;">Dear User,</p>
                            <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: center;">The interview process has been successfully completed.</p>
                            <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: center;">Please review the interview video using the button below:</p>

                            <!-- Button -->
                            <div style="text-align: center;">
                            <a href="{url}" style="display: inline-block; background: #db2777; color: #fff; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; margin: 20px auto 10px; text-align: center;">Check Interview Video</a>
                            </div>
                        </div>
                    </body>
                    </html>
                """,
            recipient=["ankita@angel-portal.com"],
            attachments=[video_path]
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
    if created:
        print("Observer Triggered")
        last_question_id = instance.last_question_id
        print("Last Question ID:", last_question_id)
        question_id = instance.question_id
        print("Question ID:", question_id)
        zoho_lead_id = instance.zoho_lead_id
        print("Zoho Lead ID:", zoho_lead_id)

        if int(last_question_id) == int(question_id):
            last_5_answers = sender.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-created_at')[:5]
            if last_5_answers.count() == 5:
                print("Exactly 5 answers found, triggering video merge.")
                async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)
            else:
                print(f"Only {last_5_answers.count()} answers found. Waiting for more.")