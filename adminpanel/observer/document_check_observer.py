# adminpanel/observer.py
import requests
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from studentpanel.models.interview_process_model import Students
from studentpanel.models.student_Interview_status import Student_Interview
from urllib.parse import quote
from studentpanel.utils.ZohoAuth import ZohoAuth
import time
import threading
from queue import Queue
from django.conf import settings
from django_q.tasks import async_task
from studentpanel.models.interview_link import StudentInterviewLink
from django.utils.timezone import now
from django.utils.timezone import localtime
import pytz
from adminpanel.utils import send_email
import base64
from datetime import timedelta
from django.contrib.auth.models import User

process_queue = Queue()
lock = threading.Lock()


class APIDataFetcher:
    def notify(self, publisher):

        # API_URL = f"https://www.zohoapis.com/crm/v2/Leads/{publisher.zoho_lead_id}/Attachments"

        API_URL = f"https://www.zohoapis.com/crm/v2/Leads/{publisher.zoho_lead_id}"

        # API_TOKEN = ZohoAuth.get_access_token()
        # print(r'API_TOKEN:', API_TOKEN)

        zoho_lead_id = publisher.zoho_lead_id
        # if zoho_lead_id == '5204268000112707003':
        # if zoho_lead_id in ['5204268000112707003', '5204268000116210079']:
        crm_id = publisher.crm_id 
        API_TOKEN = ZohoAuth.get_access_token(crm_id)
            # API_TOKEN = ZohoAuth.get_access_token()
        print(r'API_TOKEN:', API_TOKEN)
        # else:
        #     raise ValueError("Invalid Zoho Lead ID. Access token generation is not allowed.")


        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(API_URL, headers=headers)
            response.raise_for_status()
            data = response.json()
            # count = len(data['data'])
            
            # if data.get('data') and len(data['data']) > 0:
            #     highest_education_doc = data['data'][0].get('Highest_Education_Doc', [])

                # if highest_education_doc: 
                #     attachment_Id = data['data'][0]['Highest_Education_Doc'][0]['attachment_Id']
                #     file_Id = data['data'][0]['Highest_Education_Doc'][0]['file_Id']
                #     file_Name = data['data'][0]['Highest_Education_Doc'][0]['file_Name']

                #     # for item in data['data']:
                #         # file_id = item['$file_id']
                #         # parent_id = item['Parent_Id']['id']
                #         # file_name = item['File_Name']

                #     encoded_file_name = quote(file_Name)

                #     file_url = (
                #         f"https://crm.zoho.com/crm/org{publisher.crm_id}/ViewAttachment?"
                #         f"fileId={file_Id}&module=Leads&parentId={publisher.zoho_lead_id}&id={attachment_Id}"
                #         f"&name={encoded_file_name}&downLoadMode=pdfViewPlugin"
                #     )
                    # process_queue.put((file_url, publisher, API_TOKEN))
                    # process_documents()
                    # if zoho_lead_id in ['5204268000112707003', '5204268000116210079']:
                # if publisher.mindee_verification_status != 'Inprogress':
                #     # publisher.mindee_verification_status = 'Inprogress'
                #     # publisher.save(update_fields=['mindee_verification_status']) 
                #     time.sleep(10)
            async_task("adminpanel.observer.document_check_observer.process_documents_task", publisher, API_TOKEN)


        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")

# def process_documents():
#     """Manages the document processing queue to avoid overload."""
#     while not process_queue.empty():
#         with lock:  # Ensure only one task runs at a time
#             file_url, publisher, API_TOKEN = process_queue.get()

#             # Fetch document
#             file_response = requests.get(file_url)
#             if file_response.status_code != 200:
#                 print(f"❌ Failed to download file: {file_url}")
#                 continue  # Skip to the next file

#             # Process document
#             process_api_url = f"{settings.ADMIN_BASE_URL}/api/process_document"
#             data = {
#                 "first_name": publisher.first_name,
#                 "last_name": publisher.last_name,
#                 "program": publisher.program,
#                 "zoho_lead_id": publisher.zoho_lead_id,
#                 "crm_id": publisher.crm_id,
#                 "API_TOKEN": API_TOKEN,
#             }
#             files = {"document": (file_url, file_response.content, "application/pdf")}

#             try:
#                 process_response = requests.post(process_api_url, files=files, data=data)
#                 print(f"✅ Document processed: {process_response.json()}")
#             except requests.RequestException as e:
#                 print(f"❌ Processing failed: {e}")

#             time.sleep(5)  # Wait a few seconds before processing the next document



# def process_documents_task(file_url, publisher, API_TOKEN):
#     """Processes a single document in a Django Q worker."""
#     import requests
#     import time
#     from django.conf import settings

#     # Fetch document
#     file_response = requests.get(file_url)
#     if file_response.status_code != 200:
#         print(f"❌ Failed to download file: {file_url}")
#         return


#     # Process document
#     process_api_url = f"{settings.ADMIN_BASE_URL}/api/process_document"
#     data = {
#         "first_name": publisher.first_name,
#         "last_name": publisher.last_name,
#         "program": publisher.program,
#         "zoho_lead_id": publisher.zoho_lead_id,
#         "crm_id": publisher.crm_id,
#         "API_TOKEN": API_TOKEN,
#     }
#     files = {"document": (file_url, file_response.content, "application/pdf")}

#     try:
#         process_response = requests.post(process_api_url, files=files, data=data)
#         print(f"✅ Document processed: {process_response.json()}")
#     except requests.RequestException as e:
#         print(f"❌ Processing failed: {e}")

#     time.sleep(5)  # Optional delay


def process_documents_task(publisher, API_TOKEN):
    """Processes a single document in a Django Q worker."""
    import requests
    import time
    from django.conf import settings

    # Fetch document
    # try:
    #     # file_response = requests.get(file_url)
    #     # file_response.raise_for_status()  # This will raise an HTTPError for bad responses
    # except requests.RequestException as e:
    #     print(f"❌ Failed to download file: {file_url}, Error: {e}")
    #     return

    # Process document
    process_api_url = f"{settings.ADMIN_BASE_URL}/api/process_document"
    data = {
        "first_name": publisher.first_name,
        "last_name": publisher.last_name,
        "program": publisher.program,
        "zoho_lead_id": publisher.zoho_lead_id,
        "crm_id": publisher.crm_id,
        "API_TOKEN": API_TOKEN,
    }
    # files = {"document": (file_url, file_response.content, "application/pdf")}

    try:
        # Send the request
        process_response = requests.post(process_api_url,data=data)
        # Log the response status and content for debugging

        # Check if the response is JSON
        if process_response.status_code == 200:
            try:
                response_data = process_response.json()
                print(f"✅ Document processed: {response_data}")
            except ValueError:
                print(f"❌ Response is not in JSON format. Raw Response: {process_response.text}")
        else:
            print(f"❌ Failed to process document, Status Code: {process_response.status_code}")
            print(f"Response content: {process_response.text}")

    except requests.RequestException as e:
        print(f"❌ Processing failed: {e}")

    time.sleep(5)  # Optional delay


def encode_base64(data):
    """Encodes data in Base64 format (URL-safe)."""
    return base64.urlsafe_b64encode(str(data).encode()).decode()


def update_zoho_lead(crm_id, lead_id, update_data):
    try:
        print("crm_id",crm_id)
        print("lead_id",lead_id)
        print("update_data",update_data)


        access_token = ZohoAuth.get_access_token(crm_id)  # Ensure a fresh token
        url = f"https://www.zohoapis.com/crm/v2/Leads/{lead_id}"
        print("access_token",access_token)
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
        print("headers",headers)

        payload = {
            "data": [
                {
                    "id": lead_id,  # Include the lead ID in the payload
                    **update_data
                }
            ]
        }
        print("payload",payload)

        response = requests.put(url, json=payload, headers=headers)
        response_data = response.json()

        print("Response Data:", response_data)

        if response.status_code == 200 and response_data.get("data"):
            return True  # Success
        else:
            return False  # Failure

    except Exception as e:
        return False
    

@receiver(post_save, sender=Students)
def student_created_observer(sender, instance, created, **kwargs):
    if created:
        print(f"A new student was created: {instance}")
    else:
        print(f"A student was updated: {instance}")
    
    zoho_lead_id = instance.zoho_lead_id
    print(instance)

    try:
        
        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        try: 
            student_interview = Student_Interview.objects.get(zoho_lead_id=zoho_lead_id)

            if not student_interview.interview_process:
                print(student.interview_process)
                studentLinkStatus = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id)
                if studentLinkStatus.count() <= 1:
                    print(studentLinkStatus.count())

                    for student_data in studentLinkStatus:

                        update_data = {"Interview_Process": "Second Round Interview"}
                        print(update_data)
                        print(zoho_lead_id)
                        if update_zoho_lead(student.crm_id, zoho_lead_id, update_data):
                            print(studentLinkStatus.count())

                            if student_data.interview_attend == 1:
                                print("zoho_lead_id",zoho_lead_id)

                                interview_link_send_count = 2
                                encoded_zoho_lead_id = encode_base64(zoho_lead_id)
                                print("ZOHO LEAD ID",interview_link_send_count)

                                encoded_interview_link_send_count = encode_base64(interview_link_send_count)
                                print("ZOHO LEAD ID DSFS",encoded_interview_link_send_count)

                                interview_url = f'{settings.ADMIN_BASE_URL}/frontend/interview_panel/{encoded_zoho_lead_id}/{encoded_interview_link_send_count}'
                                print(interview_url)
                                new_interview_link = StudentInterviewLink.objects.create(
                                    zoho_lead_id=zoho_lead_id,
                                    interview_link=interview_url,
                                    interview_attend=0,
                                    expires_at=now() + timedelta(hours=72),
                                    interview_link_count = encoded_interview_link_send_count
                                )

                                student.is_interview_link_sent = True
                                student.interview_link_send_count = 2
                                # student.interview_process = "Second_Round_Interview"
                                student.save()

                                # # Update all required fields in Student_Interview model
                                student_interview.zoho_lead_id = zoho_lead_id
                                # student_interview.student_id = student
                                print("Student Id",)
                                student_interview.interview_process = "Second_Round_Interview"
                                student_interview.save()


                                print(new_interview_link)
                                student_name = f"{student.first_name} {student.last_name}"
                                student_email = student.email
                                student_program = student.program
                                student_zoho_lead_id = student.zoho_lead_id
                                email = student.student_manager_email.strip().lower()
                                student_manager = User.objects.filter(email__iexact=email).first()
                                student_manager_name = ''
                                if student_manager:  
                                    student_manager_name = f"{student_manager.first_name} {student_manager.last_name}".strip()
                                    print(f"student_manager_name: {student_manager_name}")
                                    student_manager_email = student_manager.email

                                interview_start = student_data.created_at
                                interview_end = student_data.expires_at

                                # Convert to Asia/Calcutta timezone
                                tz = pytz.timezone("Europe/Malta")
                                interview_start_local = localtime(interview_start).astimezone(tz)
                                interview_end_local = localtime(interview_end).astimezone(tz)

                                # Format the datetime
                                formatted_start = interview_start_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")
                                formatted_end = interview_end_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")

                                print("Start Date and time:", formatted_start)
                                print("End Date and time:", formatted_end)
                                send_email(
                                    subject="Interview Invitation for Student Interview",
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
                                                .goInterviewbtnStyle {{
                                                    display: inline-block;
                                                    background: #db2777;
                                                    color: #ffffff;
                                                    text-decoration: none;
                                                    padding: 12px 20px;
                                                    border-radius: 5px;
                                                    font-weight: bold;
                                                    margin: 20px auto 10px;
                                                    text-align: center;
                                                }}
                                                .goInterviewbtnStyle:hover {{
                                                    background-color: #0056b3;
                                                    color:#fff;
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
                                                <img src="https://ascencia-interview.com/static/img/email_template_icon/notification.png" alt="Interview Invitation" class="email-logo" />
                                                                            
                                                <p>Dear Student,</p>
                                                
                                                <p>We are pleased to invite you to participate in the following interview:</p>
                                                
                                                <p><b>Interview Details:</b></p>
                                                <p><b>Interviewer name:</b>{student_name},</p>
                                                <p><b>Start Date and time:</b>{formatted_start}</p>
                                                <p><b>End Date and time:</b>{formatted_end}</p>
                                                <p><b>Interview Round:</b>2</p>
                                                
                                                <p>Please note that you can access the interview only between the start and end times mentioned above.</p>
                                                
                                                <a href="{interview_url}" style="display: inline-block; background: #db2777; color: #fff; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; margin: 20px auto 10px; text-align: center;">Start Interview</a>

                                                <p>Best regards,<br/>Ascencia Malta</p>
                                            </div>
                                        </body>
                                    </html>
                                    """,
                                    recipient=[student_email],
                                )

                                send_email(
                                    subject="Interview Invitation Sent to Student",
                                    message=f"""
                                    <html>
                                    <head>
                                        <style>
                                            body {{
                                                font-family: Tahoma, sans-serif;
                                                background-color: #f4f4f4;
                                                padding: 20px;
                                            }}
                                            .email-container {{
                                                max-width: 600px;
                                                margin: auto;
                                                background: #ffffff;
                                                padding: 25px 30px;
                                                border-radius: 8px;
                                                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                                                border: 1px solid #ddd;
                                            }}
                                            .header {{
                                                text-align: center;
                                                margin-bottom: 20px;
                                            }}
                                            .header img {{
                                                max-height: 40px;
                                            }}
                                            h2 {{
                                                color: #2c3e50;
                                                text-align: center;
                                            }}
                                            p {{
                                                font-size: 16px;
                                                color: #333;
                                                line-height: 1.6;
                                            }}
                                            .btn {{
                                                display: inline-block;
                                                background-color: #db2777;
                                                color: #fff;
                                                padding: 10px 20px;
                                                border-radius: 5px;
                                                text-decoration: none;
                                                font-weight: bold;
                                                margin-top: 20px;
                                            }}
                                        </style>
                                    </head>
                                    <body>
                                        <div class="email-container">
                                            <div class="header">
                                                <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Ascencia Malta" />
                                            </div>

                                            <h2>Interview Invitation Sent</h2>

                                            <p>Dear <strong>{student_manager_name}</strong>,</p>

                                            <p>The interview invitation has been sent for the following student:</p>

                                            <p><strong>Student Details:</strong></p>
                                            <p><b>Name:</b> {student_name}</p>
                                            <p><b>Email:</b> {student_email}</p>
                                            <p><b>Zoho Lead ID:</b> {student_zoho_lead_id}</p>
                                            <p><b>Program:</b> {student_program}</p>
                                    

                                        

                                            <p>Regards,<br/>Ascencia Malta Team</p>
                                        </div>
                                    </body>
                                    </html>
                                    """,
                                    recipient=[student_manager_email]
                                    # recipient=["vaibhav@angel-portal.com"],  # Replace with actual student manager email
                                    # cc=["admin@example.com"],  # Optional
                                )

                                # student.save()
        except Student_Interview.DoesNotExist:
            print("Student_Interview entry does not exist")
    finally:
        print("zoho_lead_id dsfsd",zoho_lead_id)
        
        api_observer = APIDataFetcher()

        if instance.edu_doc_verification_status == 'Unverified' or (
            instance.edu_doc_verification_status == 'rejected' and instance.interview_link_send_count < 2 and instance.mindee_verification_status != 'Completed'
        ):
            api_observer.notify(instance) 

        
