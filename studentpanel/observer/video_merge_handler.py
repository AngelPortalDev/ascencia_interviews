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

    if upload_response.status_code != 201:
        return f"Error uploading video: {upload_response.text}"

    return video_id


def merge_videos(zoho_lead_id):
    uploads_folder = os.path.join(get_uploads_folder(), zoho_lead_id)
    logging.info("uploads_folder: %s", uploads_folder)

    if not os.path.exists(uploads_folder):
        return f"Error: Folder {uploads_folder} does not exist."

    video_files = sorted(
        [f for f in os.listdir(uploads_folder) if f.endswith((".webm", ".mp4", ".mov"))],
        key=lambda x: os.path.getctime(os.path.join(uploads_folder, x))
    )

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
        merge_command = f'ffmpeg -err_detect ignore_err -f concat -safe 0 -i "{list_file_path}" -c:v libvpx-vp9 -b:v 10M -c:a libopus "{output_path}"'
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

        logging.info("merge_command subprocess: %s", merge_command)
   

        # video_id = upload_to_bunnystream(output_path)
        # logging.info("video_id: %s", video_id)
        # student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        # student.bunny_stream_video_id = video_id
        # student.save()

        url = f"{settings.ADMIN_BASE_URL}/uploads/interview_videos/{zoho_lead_id}/merge_videos.webm"

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
            # cc=["admin@example.com", "hr@example.com"]  # CC recipients
        )

        # student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        # student.bunny_stream_video_id = video_id
        # student.save()
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
        last_5_answers = sender.objects.filter(zoho_lead_id=zoho_lead_id).order_by('-created_at')[:5]
        print(r'last_5_answers_count:', last_5_answers)
        if last_5_answers.count() == 5:
            print(r'last_5_answers_count text:', last_5_answers.count())
        # async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)
            async_task("studentpanel.observer.video_merge_handler.merge_videos", zoho_lead_id)
    else:
        # Handle updates to existing answers
        print(f'Answer updated: {instance}')
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