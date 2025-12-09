
from adminpanel.common_imports import *

import requests
import tempfile
import base64
import mimetypes
# import pytesseract
# import cv2
import re
import numpy as np
from pdf2image import convert_from_path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rapidfuzz import fuzz
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from mindee import Client, AsyncPredictResponse, product
from urllib.parse import parse_qs, urlparse, unquote
from difflib import SequenceMatcher
import logging
import json
from studentpanel.utils.ZohoAuth import ZohoAuth
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from studentpanel.models.interview_process_model import Students
from studentpanel.models.interview_link import StudentInterviewLink
from django.utils.timezone import now
from datetime import timedelta
from adminpanel.utils import send_email
from django.conf import settings
import os
from django.views.generic import View
from django.utils.timezone import localtime
import pytz
# Configure logging
logging.basicConfig(level=logging.INFO)
from studentpanel.models.student_Interview_status import StudentInterview
from django.core.mail import send_mail
import logging
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from datetime import timedelta

from adminpanel.helper.email_branding import get_email_branding



logger = logging.getLogger('django')



ZOHO_API_BASE_URL = "https://www.zohoapis.com/crm/v7"

# Initialize Mindee client
mindee_client = Client(api_key="4951866b395bb3fefdb1e4753c6bbd8e")

# Add endpoint configuration
my_endpoint = mindee_client.create_endpoint(
    account_name="ANKITAGAVAS",
    endpoint_name="eductional_cert_v8",
    version="1"
)

def encode_base64(data):
    """Encodes data in Base64 format (URL-safe)."""
    return base64.urlsafe_b64encode(str(data).encode()).decode()


# Define educational certificate keywords
EDUCATION_CERTIFICATE_KEYWORDS = [
    "Certificate of Completion", "Degree", "Diploma", "Bachelor", "Master",
    "Doctorate", "University", "College", "Institution", "High School",
    "Transcript", "Graduation", "Awarded", "Academic", "Educational",
    "Associate Degree", "Graduate Degree", "Postgraduate Degree", "Professional Degree",
    "Honorary Degree", "Juris Doctor", "PhD", "MD", "MBA", "MS", "MA", "BSc", "BA",
    "Vocational Certificate", "Technical Diploma", "Online Certification", "Distance Learning",
    "Course Completion", "Credential", "Accreditation", "Qualification", "Specialization",
    "Major", "Minor", "Field of Study", "Thesis", "Dissertation", "Research Paper",
    "Academic Record", "Grade Sheet", "Mark Sheet", "Enrollment Verification", "Degree Verification",
    "Proof of Education", "Educational Attainment", "Alumni", "Commencement", "Convocation"
]

RESTRICTED_FILE_NAMES = ["passport", "cv", "resume"]
FUZZY_THRESHOLD = 85  # Adjust threshold for stricter/looser matching

def serialize_field(field):
    """Recursively serializes fields into JSON serializable formats."""
    if isinstance(field, dict):  # If already a dictionary
        return {key: serialize_field(value) for key, value in field.items()}
    elif isinstance(field, list):  # If it's a list, process each element
        return [serialize_field(item) for item in field]
    else:
        return str(field) if field is not None else "N/A"

def is_restricted_filename(filename):
    filename = filename.lower()  # Normalize to lowercase
    
    for restricted_word in RESTRICTED_FILE_NAMES:
        similarity_score = fuzz.partial_ratio(restricted_word, filename)
        
        if similarity_score >= FUZZY_THRESHOLD:
            return True  # Block file if it matches closely
    
    return False

# OCR Preprocessing: Noise Reduction & Adaptive Thresholding
# def preprocess_image(image):
#     # Convert to grayscale
#     gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
#     # Apply adaptive thresholding
#     threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                                       cv2.THRESH_BINARY, 31, 2)
    
#     # Optional: Apply noise reduction
#     kernel = np.ones((1, 1), np.uint8)
#     threshold = cv2.dilate(threshold, kernel, iterations=1)
#     threshold = cv2.erode(threshold, kernel, iterations=1)
    
#     return threshold

# Extract text using optimized OCR settings
# def extract_text_from_image(image):
#     processed_image = preprocess_image(image)
#     text = pytesseract.image_to_string(processed_image, config='--psm 6 --oem 3')
#     return text.strip()

# # Convert PDF pages to images & extract text in parallel
# def extract_text_from_pdf(pdf_path):
#     images = convert_from_path(pdf_path, dpi=300)
#     extracted_text = ""

#     # Use ThreadPoolExecutor for parallel processing
#     with ThreadPoolExecutor() as executor:
#         texts = list(executor.map(extract_text_from_image, images))
#         extracted_text = " ".join(texts).strip()

#     return extracted_text if extracted_text else ""

# Extract text from an image file (PNG, JPG, JPEG)
def extract_text_from_image_file(image_path):
    image = Image.open(image_path)
    return extract_text_from_image(image)

# Keyword Matching with Fuzzy Search (Better Accuracy)
def check_educational_keywords(text):
    threshold = 90  # Adjust this to reduce false positives
    matched_keywords = []

    for keyword in EDUCATION_CERTIFICATE_KEYWORDS:
        score = fuzz.partial_ratio(keyword.lower(), text.lower())
        if score > threshold:
            matched_keywords.append(keyword)

    # Require at least 3 distinct educational keywords to classify as an educational certificate
    return len(set(matched_keywords)) >= 5


def is_certificate_filename(filename):
    certificate_keywords = [
        "certificate", "diploma", "degree", "transcript",  
        "completion", "training", "achievement", "award", "merit",  
        "qualification", "course", "certification", "graduate",  
        "honors", "recognition", "accreditation", "licensure",  
        "appreciation", "scholarship", "education", "proficiency",  
        "competency", "accomplishment", "exam", "assessment",  
        "school", "university", "college", "institution", "faculty"
    ]

    # return any(keyword in filename for keyword in certificate_keywords)

    return any(keyword.lower() in filename.lower() for keyword in EDUCATION_CERTIFICATE_KEYWORDS)



def check_eligibility(data):
    try:
        logging.info("Received data: %s", data)

        # Extracting data
        is_bachelor_certificate = data["prediction"]["fields"]["fields"].get("is_bachelor_certificate", "0") == "1"
        is_intermediate_certificate = data["prediction"]["fields"]["fields"].get("is_intermediate_certificate", "0") == "1"
        is_post_graduation_certificate = data["prediction"]["fields"]["fields"].get("is_post_graduation_certificate", "0") == "1"
        name_of_certification = data["prediction"]["fields"]["fields"].get("name_of_certification", "").lower()
        program = data["program"].lower()

        logging.info("Bachelor Certificate: %s", is_bachelor_certificate)
        logging.info("Intermediate Certificate: %s", is_intermediate_certificate)
        logging.info("Post Graduation Certificate: %s", is_post_graduation_certificate)
        logging.info("Name of Certification: %s", name_of_certification)
        logging.info("Program: %s", program)

        # Define eligibility criteria
        eligibility_criteria = {
            "bachelor": is_intermediate_certificate or is_bachelor_certificate or is_post_graduation_certificate,
            "undergraduate": is_intermediate_certificate or is_bachelor_certificate or is_post_graduation_certificate,
            "master": is_bachelor_certificate or is_post_graduation_certificate,
            "postgraduate": is_post_graduation_certificate,
        }

        logging.info("Eligibility Criteria: %s", eligibility_criteria)

        program_type = None
        for key in eligibility_criteria.keys():
            if key in program:
                program_type = key
                break

        if not program_type:
            logging.warning("Program Not Found in Criteria")
            return False

        # Special check for Computer Science programs
        cs_keywords = ["computer science", "information technology", "software engineering"]
        if "computer science" in program:
            if not any(re.search(rf"\b{cs_field}\b", name_of_certification, re.IGNORECASE) for cs_field in cs_keywords):
                logging.warning("Failed Computer Science Eligibility Check")
                return False

        # General eligibility check
        if eligibility_criteria[program_type]:
            logging.info("Eligibility Check Passed")
            return True

        logging.warning("Eligibility Check Failed")
        return False

    except KeyError as e:
        logging.error("Missing key in data: %s", e)
        return False
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        return False
    

def name_match_ratio(name1, name2):
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


def update_zoho_lead(crm_id, lead_id, update_data):
    try:
        access_token = ZohoAuth.get_access_token(crm_id)  # Ensure a fresh token
        url = f"https://www.zohoapis.com/crm/v2/Leads/{lead_id}"
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "data": [
                {
                    "id": lead_id,  # Include the lead ID in the payload
                    **update_data
                }
            ]
        }

        response = requests.put(url, json=payload, headers=headers)
        response_data = response.json()

        print("Response Data:", response_data)

        if response.status_code == 200 and response_data.get("data"):
            logging.info(f"Zoho Lead {lead_id} updated successfully")
            return True  # Success
        else:
            logging.error(f"Failed to update Zoho Lead {lead_id}: {response_data}")
            return False  # Failure

    except Exception as e:
        logging.error(f"Error updating Zoho Lead {lead_id}: {e}")
        return False
    


# def send_email(interview_url, student_name, student_manager_email):
#     sender_email = "abdullah@angel-portal.com"
#     receiver_email = "abdullah@angel-portal.com"
#     student_manager_email = f"student_manager_email" 
    
#     subject = "Zoho Lead Update Notification"    
#     body = f"""
#         <html>
#         <body>
#             <p>Lead update was successful.</p>
#             <p>Click the link below to proceed:</p>
#             <p><a href='{interview_url}'>Go to Interview</a></p>
#         </body>
#         </html>
#     """

    
#     student_manager_body = f"""
#         <html>
#         <head>
#             <style>
#                 body {{
#                     font-family: Arial, sans-serif;
#                     background-color: #f4f4f4;
#                     padding: 20px;
#                     text-align: center;
#                 }}
#                 .email-container {{
#                     max-width: 600px;
#                     margin: auto;
#                     background: #ffffff;
#                     padding: 20px;
#                     border-radius: 8px;
#                     box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
#                 }}
#                 h2 {{
#                     color: #2c3e50;
#                 }}
#                 p {{
#                     color: #555555;
#                     font-size: 16px;
#                     line-height: 1.6;
#                 }}
#                 .btn {{
#                     display: inline-block;
#                     background: #007bff;
#                     color: #ffffff;
#                     text-decoration: none;
#                     padding: 10px 20px;
#                     border-radius: 5px;
#                     font-weight: bold;
#                     margin-top: 10px;
#                 }}
#                 .btn:hover {{
#                     background: #0056b3;
#                 }}
#             </style>
#         </head>
#         <body>
#             <div class="email-container">
#                 <h2>Document Verification Completed</h2>
#                 <p>Dear {student_manager_name},</p>
#                 <p>The document verification process for <strong>{student_name}</strong> has been successfully completed.</p>
#                 <p>Click the button below to review the details:</p>
#                 <a href='http://127.0.0.1:8000/verification' class="btn">View Verification Details</a>
#             </div>
#         </body>
#         </html>
#     """




#     msg = MIMEMultipart()
#     msg["From"] = sender_email
#     msg["To"] = receiver_email
#     msg["Subject"] = subject
#     msg.attach(MIMEText(body, "html"))

#     try:
#         # ✅ Use the correct SMTP server for your email provider
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Change to your email provider's SMTP
#             server.starttls()
#             server.login(sender_email, "iuljudjtemskylkl")  # Use an app password if required

#             # Email to the user
#             msg_user = MIMEMultipart()
#             msg_user["From"] = sender_email
#             msg_user["To"] = receiver_email
#             msg_user["Subject"] = subject
#             msg_user.attach(MIMEText(body, "html"))
#             server.sendmail(sender_email, receiver_email, msg_user.as_string())
#             # server.sendmail(sender_email, receiver_email, msg.as_string())


#             # Email to the Student Manager
#             msg_manager = MIMEMultipart()
#             msg_manager["From"] = sender_email
#             msg_manager["To"] = student_manager_email
#             msg_manager["Subject"] = "Document Verification Update"
#             msg_manager.attach(MIMEText(student_manager_body, "html"))
#             server.sendmail(sender_email, student_manager_email, msg_manager.as_string())
        
#         print("Email sent successfully")
#     except Exception as e:
#         print(f"Email sending failed: {str(e)}")



@csrf_exempt
def process_document(request):

    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    # try:
    # Retrieve form data
    try:
        # uploaded_file = request.FILES.get("document")
        zoho_first_name = request.POST.get("first_name", "").strip()
        zoho_last_name = request.POST.get("last_name", "").strip()
        program = request.POST.get("program", "").strip()
        zoho_lead_id = request.POST.get("zoho_lead_id", "").strip()
        crm_id = request.POST.get("crm_id", "").strip()
        API_TOKEN = request.POST.get("API_TOKEN", "")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    student = Students.objects.get(zoho_lead_id=zoho_lead_id)
    # student.mindee_verification_status = "Inprogress"
    # student.save()

    email = student.student_manager_email.strip().lower()
    student_manager = User.objects.filter(email__iexact=email).first()
    student_manager_name = ''
    if student_manager:  
        student_manager_name = f"{student_manager.first_name} {student_manager.last_name}".strip()
        print(f"student_manager_name: {student_manager_name}")
        student_manager_email = student_manager.email

    print(f"Received first_name: {zoho_first_name}, last_name: {zoho_last_name}, program: {program}")

        # second comment

        # if not uploaded_file:
        #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        #     student.verification_failed_reason = "No document uploaded"
        #     student.mindee_verification_status = "Completed"
        #     student.save()
        #     return JsonResponse({"error": "No document uploaded"}, status=400)

        # Validate file name
        # filename = re.search(r"&name=([^&]+)", uploaded_file.name.lower())
        # filename = unquote(filename.group(1)) if filename else "unknown.pdf"

        # filename_match = re.search(r"&name=([^&]+)", uploaded_file.name.lower())
        # filename = unquote(filename_match.group(1)) if filename_match else "unknown.pdf"

        # print(f"Processed filename: {filename}")

        # if is_restricted_filename(filename):
        #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        #     student.verification_failed_reason = "Invalid file. Passport, CV, and Resume files are not allowed."
        #     student.mindee_verification_status = "Completed"
        #     student.save()
        #     return JsonResponse({"error": "Invalid file. Passport, CV, and Resume files are not allowed."}, status=400)

        # Construct URL
        # [REMOVED] Skipping Zoho CRM attachment parsing and document download
        # third commented

        # url = f"https://crm.zoho.com/crm/org771809603/{uploaded_file}"
        # query_params = parse_qs(urlparse(url).query)

        # # Extract parent_id and file_id
        # parent_id, file_id = query_params.get("parentId", [""])[0], query_params.get("id", [""])[0]
        # file_url = f"https://www.zohoapis.com/crm/v7/Leads/{parent_id}/Attachments/{file_id}"

        # # Download the file
        # headers = {"Authorization": f"Zoho-oauthtoken {API_TOKEN}", "User-Agent": "Mozilla/5.0"}
        # response = requests.get(file_url, headers=headers, allow_redirects=True)

        # if response.status_code != 200:
        #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        #     student.verification_failed_reason = "Failed to download file"
        #     student.mindee_verification_status = "Completed"
        #     student.save()
        #     return JsonResponse({"error": f"Failed to download file, Status Code: {response.status_code}"}, status=400)

        # Save the downloaded file temporarily
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
    #     temp_file.write(response.content)
    #     temp_file_path = temp_file.name

    # print(f"File downloaded and saved at: {temp_file_path}")

        # 4th comment
        # Validate MIME type
        # mime_type = uploaded_file.content_type
        # if mime_type not in ["application/pdf", "image/png", "image/jpeg", "image/jpg"]:
        #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        #     student.verification_failed_reason = "Invalid file type. Only PDF, PNG, JPG, and JPEG files are supported."
        #     student.mindee_verification_status = "Completed"
        #     student.save()
        #     return JsonResponse({"error": "Invalid file type. Only PDF, PNG, JPG, and JPEG files are supported."}, status=400)

        # Extract text
        # extracted_text = (
        #     extract_text_from_pdf(temp_file_path) if mime_type == "application/pdf"
        #     else extract_text_from_image_file(temp_file_path)
        # )

        # if not extracted_text:
        #     return JsonResponse({"error": "Text extraction failed. The document might be too blurry or contain no text."}, status=400)

        # # Check if the document is an educational certificate
        # if not (check_educational_keywords(extracted_text) or is_certificate_filename(filename)):
        #     return JsonResponse({"message": "Error", "is_education_certificate": False}, status=200)


        # if not is_certificate_filename(filename):
        #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        #     student.verification_failed_reason = "Invalid document name. Please upload a file with a recognizable education certificate title."
        #     student.mindee_verification_status = "Completed"
        #     student.save()
        #     return JsonResponse({"message": "Error", "is_education_certificate": False}, status=200)

        # Process document with Mindee

        # 5 th comment
        # try:
            # input_doc = mindee_client.source_from_path(temp_file_path)
            # result: AsyncPredictResponse = mindee_client.enqueue_and_parse(product.GeneratedV1, input_doc, endpoint=my_endpoint)

            # prediction = result.document.inference.prediction
            # serialized_prediction = serialize_field(vars(prediction))

            # data = {"prediction": {"fields": serialized_prediction}, "program": program}
            # # print("data prediction:",data)

            # # Name similarity check
            # mindee_first_name = data["prediction"]["fields"]["fields"].get("first_name", "").strip().lower()
            # mindee_last_name = data["prediction"]["fields"]["fields"].get("last_name", "").strip().lower()
            # zoho_full_name, mindee_full_name = f"{zoho_first_name} {zoho_last_name}".lower(), f"{mindee_first_name} {mindee_last_name}".lower()

            # if name_match_ratio(zoho_full_name, mindee_full_name) < 0.70:
            #     update_data = {"Interview_Process": "First Round Interview Hold"}
                
            #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
            #     student.mindee_verification_status = "Completed"
            #     student.edu_doc_verification_status = "rejected"
            #     student.verification_failed_reason = "Name Not Matched"

            #     print("verification_failed_reason",student.verification_failed_reason)
            #     student.save()
            #     # if update_zoho_lead(crm_id, zoho_lead_id, update_data):
            #     #     print("Lead updated successfully")
            #     # else:
            #     #     print("Lead update failed")
                
            #     # Student Manager Notification Email (Document Rejected)
            #     send_email(
            #         subject="Document Verification Rejected",
            #         message=f"""
            #             <html>
            #             <head>
            #                 <style>
            #                     body {{
            #                         font-family: Tahoma !important;
            #                         background-color: #f4f4f4;
            #                         padding: 20px;
            #                         text-align: left;
            #                     }}
            #                     .email-container {{
            #                         max-width: 600px;
            #                         margin: auto;
            #                         background: #ffffff;
            #                         padding: 20px;
            #                         border-radius: 8px;
            #                         box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            #                         border: 1px solid #ddd;
            #                     }}
            #                     .header {{
            #                         text-align: center;
            #                         padding-bottom: 20px;
            #                         border-bottom: 1px solid #ddd;
            #                     }}
            #                     .header img {{
            #                         max-width: 150px;
            #                         display:flex;
            #                         margin:0 auto;
            #                     }}
            #                     h2 {{
            #                         color: #c0392b;  /* Red color for rejection */
            #                     }}
            #                     p {{
            #                         color: #555555;
            #                         font-size: 16px;
            #                         line-height: 1.6;
            #                     }}
            #                     .btn {{
            #                         display: inline-block;
            #                         background: #c0392b;  /* Red button */
            #                         color: #FFFFFF;
            #                         text-decoration: none;
            #                         padding: 10px 20px;
            #                         border-radius: 5px;
            #                         font-weight: bold;
            #                         margin-top: 10px;
            #                     }}
            #                     .btn:hover {{
            #                         background: #a93226;
            #                         color: #FFFFFF;
            #                     }}
            #                     .email-logo {{
            #                         max-width: 300px;
            #                         height: auto;
            #                         width: 100%;
            #                         margin-bottom: 20px;
            #                         display: flex;
            #                         justify-content: center;
            #                         margin: 0 auto;
            #                     }}
            #                     .logo_style{{
            #                         height:40px;
            #                         width:auto;
            #                     }}
            #                     @media only screen and (max-width: 600px) {{
            #                                     .email_logo_lead {{
            #                                         width: 100% !important;
            #                                     }}
            #                             }}
            #                 </style>
            #             </head>
            #             <body style="background-color: #f4f4f4; font-family: Tahoma, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh;">
                          
            #                             <div class="email-container" style="background: #ffffff; max-width: 600px; width: 100%; padding: 30px 25px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); border: 1px solid #ddd; box-sizing: border-box; margin:0 auto;">
            #                                 <div class="header" style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee;">
            #                                     <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Ascencia Malta" class="logo_style" style="height: 40px; width: auto; margin-bottom: 10px;">
            #                                 </div>
            #                                 <img src="https://ascencia-interview.com/static/img/email_template_icon/doc_rejected.png" 
            #                                     alt="Document Rejected" class="email_logo_lead" style="width: 50%; display: block; margin: 20px auto;"/>
                                         
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Dear <span style="font-weight:bold">{student_manager_name},</span></p>
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">The document verification process for <strong>{zoho_full_name}</strong> has been <strong>rejected</strong>.</p>
                                            
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;"><strong>Next Steps:</strong> Please review the reason for rejection and ask the student to re-upload the correct documents.</p>
                                            
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Click below to review rejection details:</p>
            #                                   <div style="text-align: left;">
            #                                     <a href="https://ascencia-interview.com/studentmanagerpanel/student/{zoho_lead_id}/" class="btn" style="display: inline-block; background: #db2777; color: #fff; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; margin: 20px auto 10px; text-align: left;">View Rejection Details</a>
            #                                   </div>
            #                                   <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left; margin-top: 30px;">
            #                                         Best regards,<br/>Ascencia Malta
            #                                     </p>
            #                             </div>
                                        
                                    
            #             </body>
            #             </html>
            #         """,
            #         recipient=["vaibhav@angel-portal.com"],
            #         # cc=["admin@example.com", "hr@example.com"]  # Optional CC recipients
            #     )
            #     return JsonResponse({"message": "Success", "result": False}, status=200)

            # # Completion check
            # if not data["prediction"]["fields"]["fields"].get("completion_remark"):
            #     update_data = {"Interview_Process": "First Round Interview Hold"}
                
            #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
            #     student.mindee_verification_status = "Completed"
            #     student.edu_doc_verification_status = "rejected"
            #     student.verification_failed_reason = "Criteria not matched"
            #     student.save()
            #     if update_zoho_lead(crm_id, zoho_lead_id, update_data):
            #         print("Lead updated successfully")
            #     else:
            #         print("Lead update failed")


            #     # Student Manager Notification Email (Document Rejected)
            #     send_email(
            #         subject="Document Verification Rejected",
            #         message=f"""
            #             <html>
            #             <head>
            #                 <style>
            #                     body {{
            #                         font-family: Tahoma !important;
            #                         background-color: #f4f4f4;
            #                         padding: 20px;
            #                         text-align: left;
            #                     }}
            #                     .email-container {{
            #                         max-width: 600px;
            #                         margin: auto;
            #                         background: #ffffff;
            #                         padding: 20px;
            #                         border-radius: 8px;
            #                         box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            #                         border: 1px solid #ddd;
            #                     }}
            #                     .header {{
            #                         text-align: center;
            #                         padding-bottom: 20px;
            #                         border-bottom: 1px solid #ddd;
            #                     }}
            #                     .header img {{
            #                         max-width: 150px;
            #                         display:flex;
            #                         margin:0 auto;
            #                     }}
            #                     h2 {{
            #                         color: #c0392b;  /* Red color for rejection */
            #                     }}
            #                     p {{
            #                         color: #555555;
            #                         font-size: 16px;
            #                         line-height: 1.6;
            #                     }}
            #                     .btn {{
            #                         display: inline-block;
            #                         background: #c0392b;  /* Red button */
            #                         color: #ffffff;
            #                         text-decoration: none;
            #                         padding: 10px 20px;
            #                         border-radius: 5px;
            #                         font-weight: bold;
            #                         margin-top: 10px;
            #                     }}
            #                     .btn:hover {{
            #                         background: #a93226;
            #                     }}
            #                     .logo_style{{
            #                         height:40px;
            #                         width:auto;
            #                     }}
            #                     .email-logo {{
            #                         max-width: 300px;
            #                         height: auto;
            #                         width: 100%;
            #                         margin-bottom: 20px;
            #                         display: flex;
            #                         justify-content: center;
            #                         margin: 0 auto;
            #                     }}
            #                     @media only screen and (max-width: 600px) {{
            #                                     .email_logo_lead {{
            #                                         width: 100% !important;
            #                                     }}
            #                             }}
            #                 </style>
            #             </head>
            #             <body style="background-color: #f4f4f4; font-family: Tahoma, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh;">
                        
            #                             <div class="email-container" style="background: #ffffff; max-width: 600px; width: 100%; padding: 30px 25px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); border: 1px solid #ddd; box-sizing: border-box; margin:0 auto;">
            #                                 <div class="header" style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee;">
            #                                     <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Ascencia Malta" class="logo_style" style="height: 40px; width: auto; margin-bottom: 10px;">
            #                                 </div>
            #                                 <img src="https://ascencia-interview.com/static/img/email_template_icon/doc_rejected.png" 
            #                                     alt="Document Rejected" class="email_logo_lead" style="width: 50%; display: block; margin: 20px auto;"/>
            #                                 <h2 style="color: #2c3e50; text-align: center;">Document Verification Rejected</h2>
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Dear <span style="font-weight:bold">{student_manager_name},</span></p>
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">The document verification process for <strong>{zoho_full_name}</strong> has been <strong>rejected</strong>.</p>
                                            
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;"><strong>Next Steps:</strong> Please review the reason for rejection and ask the student to re-upload the correct documents.</p>
                                            
            #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Click below to review rejection details:</p>
            #                                   <div style="text-align: left;">
            #                                     <a href="https://ascencia-interview.com/studentmanagerpanel/student/{zoho_lead_id}/" class="btn" style="display: inline-block; background: #db2777; color: #fff; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; margin: 20px auto 10px; text-align: left;">View Rejection Details</a>
            #                                   </div>
            #                                    <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left; margin-top: 30px;">
            #                                         Best regards,<br/>Ascencia Malta
            #                                     </p>
            #                                 </div>
                                    
            #             </body>
            #             </html>
            #         """,
            #         recipient=["vaibhav@angel-portal.com"],
            #         # cc=["admin@example.com", "hr@example.com"]  # Optional CC recipients
            #     )

            #     return JsonResponse({"message": "Success", "result": False}, status=200)

            # result = check_eligibility(data)
            

            # if result:
    update_data = {"Interview_Process": "First Round Interview"}

    if update_zoho_lead(crm_id, zoho_lead_id, update_data):
        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        student.mindee_verification_status = "Completed"
        student.edu_doc_verification_status = "approved"
        student.verification_failed_reason = ""
        student.is_interview_link_sent = True
        student.interview_link_send_count = 1
        # student.interview_process = "Second_Round_Interview"
        student.save()                   

        encoded_zoho_lead_id = encode_base64(zoho_lead_id)
        encoded_interview_link_send_count = encode_base64(student.interview_link_send_count)
        interview_url = f'{settings.ADMIN_BASE_URL}/frontend/interview_panel/{encoded_zoho_lead_id}/{encoded_interview_link_send_count}'
        print(interview_url)
        
        interview_link, created = StudentInterviewLink.objects.update_or_create(
            zoho_lead_id=zoho_lead_id,
            defaults={
                "interview_link_count" : encoded_interview_link_send_count,
                "interview_link": interview_url,
                "expires_at": now() + timedelta(hours=72),
            }
        )

        # student = Students.objects.get(zoho_lead_id=zoho_lead_id)
        student_name = f"{student.first_name} {student.last_name}"
        student_email = student.email
        student_zoho_lead_id = student.zoho_lead_id
        student_program=student.program

        studentLinkStatus = StudentInterviewLink.objects.get(zoho_lead_id=zoho_lead_id)
        interview_start = studentLinkStatus.created_at
        interview_end = studentLinkStatus.expires_at


        try:
            student_interview_status = StudentInterview.objects.get(zoho_lead_id=zoho_lead_id)
            student_interview_status.interview_process="Second_Round_Interview"
            student_interview_status.save()
        except StudentInterview.DoesNotExist:
            student_interview = StudentInterview.objects.create(
                zoho_lead_id=zoho_lead_id,
                # student_id=student,
                interview_process="Second_Round_Interview"
            )
                        

        # Convert to Asia/Calcutta timezone
        tz = pytz.timezone("Europe/Malta")
        interview_start_local = localtime(interview_start).astimezone(tz)
        interview_end_local = localtime(interview_end).astimezone(tz)
        studentLinkStatus.created_at = interview_start_local
        studentLinkStatus.expires_at = interview_end_local
        studentLinkStatus.save(update_fields=["created_at", "expires_at"])

        # Format the datetime
        formatted_start = interview_start_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")
        formatted_end = interview_end_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")

        print("Start Date and time:", formatted_start)
        print("End Date and time:", formatted_end)
        # interview_link = StudentInterviewLink.objects.create(
        #     zoho_lead_id=zoho_lead_id,
        #     interview_link=interview_url,
        #     expires_at=now() + timedelta(hours=72)
        # )
        
        # send_email(interview_url, zoho_full_name, 'student@manager.com')
        
        # 2. First: Send document verification & interview email
        # Student Manager Notification Email
        # send_email(
        #     subject="Document Verification & Interview Link",
        #     message=f"""
        #         <html>
        #         <head>
        #             <style>
        #                 body {{
        #                     font-family: Tahoma !important;
        #                     background-color: #f4f4f4;
        #                     padding: 20px;
        #                     text-align: left;
        #                 }}
        #                 .email-container {{
        #                     max-width: 600px;
        #                     margin: auto;
        #                     background: #ffffff;
        #                     padding: 20px;
        #                     border-radius: 8px;
        #                     box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        #                 }}
        #                 .header {{
        #                     text-align: center;
        #                     padding-bottom: 20px;
        #                     border-bottom: 1px solid #ddd; 
        #                 }}
        #                 .header img {{
        #                     max-width: 150px;
        #                 }}
        #                 h2 {{
        #                     color: #2c3e50;
        #                 }}
        #                 p {{
        #                     color: #555555;
        #                     font-size: 16px;
        #                     line-height: 1.6;
        #                 }}
        #                 .btn {{
        #                     display: inline-block;
        #                     background: #db2777;
        #                     color: #FFFFFF;
        #                     text-decoration: none;
        #                     padding: 10px 20px;
        #                     border-radius: 5px;
        #                     font-weight: bold;
        #                     margin-top: 10px;
        #                 }}
        #                 .btn:hover {{
        #                     background: #0056b3;
        #                     color: #FFFFFF;
        #                 }}
        #                 .email-logo {{
        #                     max-width: 300px;
        #                     height: auto;
        #                     width: 100%;
        #                     margin-bottom: 20px;
        #                     display: flex;
        #                     justify-content: center;
        #                     margin: 0 auto;
        #                 }}
        #                 .logo_style{{
        #                     height:40px;
        #                     width:auto;
        #                 }}
        #                 @media only screen and (max-width: 600px) {{
        #                             .email_logo_lead {{
        #                                 width: 100% !important;
        #                             }}
        #                     }}
        #             </style>
        #         </head>
        #         <body style="background-color: #f4f4f4; font-family: Tahoma, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh;">
                    
        #                         <div class="email-container" style="background: #ffffff; max-width: 600px; width: 100%; padding: 30px 25px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); border: 1px solid #ddd; box-sizing: border-box; margin:0 auto;">
        #                             <div class="header" style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee;">
        #                                 <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Company Logo" class="logo_style" style="height: 40px; width: auto; margin-bottom: 10px;">
        #                             </div>
        #                             <img src="https://ascencia-interview.com/static/img/email_template_icon/doc_verified.png" alt="Document Verified" class="email-logo" class="email_logo_lead" style="width: 50%; display: block; margin: 20px auto;"/>
        #                             <h2 style="color: #2c3e50; text-align: center;">Document Verification Completed</h2>
        #                             <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Dear <span style="font-weight:bold">{student_manager_name},</span></p>
        #                             <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">The document verification process for <strong>{zoho_full_name}</strong> has been successfully completed.</p>
                                    
        #                             <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;"><strong>Next Step:</strong> The student is now eligible for the interview process.</p>
                                    
        #                             <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left;">Click below to review verification details:</p>
        #                                 <div style="text-align: left;">
        #                                 <a href="https://ascencia-interview.com/studentmanagerpanel/student/{zoho_lead_id}/" class="btn" style="display: inline-block; background: #db2777; color: #fff; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; margin: 20px auto 10px; text-align: center;">View Verification Details</a>
        #                                 </div>
        #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: left; margin-top: 30px;">
        #                                 Best regards,<br/>Ascencia Malta
        #                             </p>
        #                         </div>
                            
        #         </body>
        #         </html>
        #     """,
        #     recipient=["vaibhav@angel-portal.com"],
        #     # cc=["admin@example.com", "hr@example.com"]  # Optional CC recipients
        # )
        # 3. Then: Send Zoho Lead Update Notification email
        # student
        logo_url, company_name = get_email_branding(crm_id)
        # logo_url = "https://dev.ascencia-interview.com/static/img/email_template_icon/cdp_india_logo.png"
        # company_name = "College De Paris"
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
                            .goInterviewbtnStyle {{
                                display: inline-block;
                                background: #db2777;
                                color: #fff;
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
                                <img src="{logo_url}" alt="Ascencia Malta" />
                            </div>
                            <img src="https://ascencia-interview.com/static/img/email_template_icon/notification.png" alt="Interview Invitation" class="email-logo" />
                            
                            <h2>Interview Invitation for Student Interview  {student_name},</h2>
                            
                            <p>Dear Student,</p>
                            
                            <p>We are pleased to invite you to participate in the following interview:</p>
                            
                            <p><b>Interview Details:</b></p>
                            <p><b>Interviewer name:</b>{student_name},</p>
                            <p><b>Start Date and time:</b>{formatted_start}</p>
                            <p><b>End Date and time:</b>{formatted_end}</p>
                            
                            <p>Please note that you can access the interview only between the start and end times mentioned above.</p>
                            
                            <a href="{interview_url}" style="display: inline-block; background: #db2777; color: #fff; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; margin: 20px auto 10px; text-align: center;">Start Interview</a>

                                        <p>Best regards,<br/>{company_name}</p>
                                    </div>
                                </body>
                            </html>
                            """,
                            # recipient=["vaibhav@angel-portal.com"],
                            recipient=[student_email],
                            reply_to=[student_manager_email]  # ✅ Ensures replies go to student manager too
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
                                                max-height: 70px;
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
                                                <img src="{logo_url}" alt="Ascencia Malta" />
                                            </div>

                                            <h2>Interview Invitation Sent</h2>

                                            <p>Dear <strong>{student_manager_name}</strong>,</p>

                                            <p>The interview invitation has been sent for the following student:</p>

                                            <p><strong>Student Details:</strong></p>
                                            <p><b>Name:</b> {student_name}</p>
                                            <p><b>Email:</b> {student_email}</p>
                                            <p><b>Zoho Lead ID:</b> {student_zoho_lead_id}</p>
                                            <p><b>Program:</b> {student_program}</p>
                                            <p><b>Start Date and time:</b>{formatted_start}</p>
                                            <p><b>End Date and time:</b>{formatted_end}</p>
                                            <p><b>Interview Link : </b><a href="{interview_url}" target="_blank">{interview_url}</a></p>
                                        

                                            <p>Regards,<br/>{company_name} Team</p>
                                        </div>
                                    </body>
                                    </html>
                                    """,
                                    recipient=[student_manager_email]
                                    # recipient=["vaibhav@angel-portal.com"],  # Replace with actual student manager email
                                    # cc=["admin@example.com"],  # Optional
                                )


        
        print("Lead updated successfully")
        return JsonResponse({"message": "Success", "result": True}, status=200)
    else:
        print("Lead update failed")
        return JsonResponse({"error": "Zoho update failed"}, status=500)
# else:
    #     update_data = {"Interview_Process": "First Round Interview Hold"}
        
    #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
    #     student.mindee_verification_status = "Completed"
    #     student.edu_doc_verification_status = "rejected"
    #     student.verification_failed_reason = "Criteria not matched"
    #     student.save()
    #     if update_zoho_lead(crm_id, zoho_lead_id, update_data):
    #         print("Lead updated successfully")
    #     else:
    #         print("Lead update failed")

    #     # Student Manager Notification Email (Document Rejected)
    #     send_email(
    #         subject="Document Verification Rejected",
    #         message=f"""
    #             <html>
    #             <head>
    #                 <style>
    #                     body {{
    #                         font-family: Tahoma !important;
    #                         background-color: #f4f4f4;
    #                         padding: 20px;
    #                         text-align: left;
    #                     }}
    #                     .email-container {{ 
    #                         max-width: 600px;
    #                         margin: auto;
    #                         background: #ffffff;
    #                         padding: 20px;
    #                         border-radius: 8px;
    #                         box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    #                         border: 1px solid #ddd;
    #                     }}
    #                     .header {{
    #                         text-align: center;
    #                         padding-bottom: 20px;
    #                         border-bottom: 1px solid #ddd;
    #                     }}
    #                     .header img {{
    #                         max-width: 150px;
    #                         display:flex;
    #                         margin:0 auto;
    #                     }}
    #                     h2 {{
    #                         color: #c0392b;  /* Red color for rejection */
    #                     }}
    #                     p {{
    #                         color: #555555;
    #                         font-size: 16px;
    #                         line-height: 1.6;
    #                     }}
    #                     .btn {{
    #                         display: inline-block;
    #                         background: #c0392b;  /* Red button */
    #                         color: #FFFFFF;
    #                         text-decoration: none;
    #                         padding: 10px 20px;
    #                         border-radius: 5px;
    #                         font-weight: bold;
    #                         margin-top: 10px;
    #                     }}
    #                     .btn:hover {{
    #                         background: #a93226;
    #                         color: #FFFFFF;
    #                     }}
    #                     .email-logo {{
    #                         max-width: 300px;
    #                         height: auto;
    #                         width: 100%;
    #                         margin-bottom: 20px;
    #                         display: flex;
    #                         justify-content: center;
    #                         margin: 0 auto;
    #                     }}
    #                     .logo_style{{
    #                         height:40px;
    #                         width:auto;
    #                     }}
    #                     @media only screen and (max-width: 600px) {{
    #                                         .email_logo_lead {{
    #                                             width: 100% !important;
    #                                         }}
    #                                 }}
    #                 </style>
    #             </head>
    #             <body style="background-color: #f4f4f4; font-family: Tahoma, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh;">
                    
    #                             <div class="email-container" style="background: #ffffff; max-width: 600px; width: 100%; padding: 30px 25px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); border: 1px solid #ddd; box-sizing: border-box; margin:0 auto;">
    #                                 <div class="header" style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee;">
    #                                     <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Ascencia Malta" class="logo_style" style="height: 40px; width: auto; margin-bottom: 10px;">
    #                                 </div>
    #                                 <img src="https://ascencia-interview.com/static/img/email_template_icon/doc_rejected.png" 
    #                                     alt="Document Rejected" class="email_logo_lead" style="width: 50%; display: block; margin: 20px auto;"/>
    #                                 <h2 style="color: #2c3e50; text-align: center;">Document Verification Rejected</h2>
    #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: center;">Dear <span style="font-weight:bold">{student_manager_name},</span></p>
    #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: center;">The document verification process for <strong>{zoho_full_name}</strong> has been <strong>rejected</strong>.</p>
                                    
    #                                 <p style="color: #555; font-size: 16px; line-height: 1.6; text-align: center;">Click below to review rejection details:</p>
    #                                     <div style="text-align: center;">
    #                                     <a href="https://ascencia-interview.com/studentmanagerpanel/student/{zoho_lead_id}/" class="btn"  style="display: inline-block; background: #db2777; color: #fff; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; margin: 20px auto 10px; text-align: center;">View Rejection Details</a>
    #                                     </div>
    #                             </div>
                            
    #             </body>
    #             </html>
    #         """,
    #         recipient=["vaibhav@angel-portal.com"],
    #         # cc=["admin@example.com", "hr@example.com"]  # Optional CC recipients
    #     )
    #     return JsonResponse({"message": "Success", "result": result}, status=200)


    #     except Exception as e:
    #         student = Students.objects.get(zoho_lead_id=zoho_lead_id)
    #         student.verification_failed_reason = "Mindee API processing failed"
    #         student.mindee_verification_status = "Completed"
    #         student.save()
    #         return JsonResponse({"error": f"Mindee API processing failed: {str(e)}"}, status=500)

    # except Exception as e:
    #     student = Students.objects.get(zoho_lead_id=zoho_lead_id)
    #     student.verification_failed_reason = "unexpected error occurred"
    #     student.mindee_verification_status = "Completed"
    #     student.save()
    #     return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    
def fetch_interview_questions(request, crm_id):
    try:
        # Fetch 2 random questions from commonquestions
        if crm_id:
            common_questions = list(CommonQuestion.objects.filter(crm_id=crm_id).order_by('id')[:2])
        else:
            common_questions = []

        # Fetch 3 random questions from questions
        # customized_questions = list(Question.objects.order_by('id')[:3])  

        # Combine questions
        # questions_list = common_questions + customized_questions
        questions_list = common_questions

        # Convert to JSON serializable format
        data = [
            {
                'id': q.id,
                'question': q.question,
                'type': 'common' if isinstance(q, CommonQuestion) else 'customized'
            } 
            for q in questions_list
        ]

        return JsonResponse({'status': 'success', 'questions': data})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
class FrontendAppView(View):
    def get(self, request):
        try:
            with open(os.path.join(settings.BASE_DIR, 'frontend', 'build', 'index.html'), encoding='utf-8') as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            return HttpResponse(
                "React build index.html not found! Please build your React app.",
                status=501,
            )
        
# def send_interview_reminders(zoho_lead_id):
#     print(">>> Running reminder check <<<")
#     now_time = now()
#     expiry_threshold = now_time + timedelta(hours=24)

#     pending_students = StudentInterviewLink.objects.filter(
#     zoho_lead_id=zoho_lead_id,
#     interview_attend=False,
#     is_expired=False,
#     reminder_sent=False,
#     expires_at__lte=expiry_threshold,
#     expires_at__gte=now_time
#     )

#     count = pending_students.count()
#     print(f">>> Found {count} students <<<")


#     for student in pending_students:
#         # student_name = getattr(student.student, 'full_name', 'Student')
#         student_obj = Students.objects.filter(zoho_lead_id=student.zoho_lead_id).first()
#         student_name = student_obj.first_name
#         student_email = student_obj.email
#         print("Email",student_email)
#         student_manager_name = getattr(getattr(student_obj, 'student_manager', None), 'full_name', 'Manager')
#         interview_url = student.interview_link
#         studentLinkStatus = StudentInterviewLink.objects.get(zoho_lead_id=zoho_lead_id)
#         interview_start = studentLinkStatus.created_at
#         interview_end = studentLinkStatus.expires_at
#          # Convert to Asia/Calcutta timezone
#         tz = pytz.timezone("Europe/Malta")
#         interview_start_local = localtime(interview_start).astimezone(tz)
#         interview_end_local = localtime(interview_end).astimezone(tz)

#         # Format the datetime
#         formatted_start = interview_start_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")
#         formatted_end = interview_end_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")

#         # start = student.start_time.strftime('%d %B %Y - %I:%M%p') + " (Europe/Malta)"
#         # end = student.expires_at.strftime('%d %B %Y - %I:%M%p') + " (Europe/Malta)"
#         # to_email = [getattr(student_obj, 'email', 'vaibhav@angel-portal.com')]
#         to_email = ["vaibhav@angel-portal.com"]
#         # to_email = [student_email]
#         subject = "sent reminder  for student"
#         from_email =""

#         text_content = f"""Reminder: Interview for {student_name} expires in 24 hours. Visit: {interview_url}"""
#         student1 = Students.objects.get(zoho_lead_id=zoho_lead_id)

#         crm_id = student1.crm_id
#         logo_url, company_name = get_email_branding(crm_id)
#         html_content = f"""
#         <html>
#           <body style="background-color: #f4f4f4; font-family: Tahoma, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh;">
#             <div style="background: #ffffff; max-width: 600px; width: 100%; padding: 30px 25px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border: 1px solid #ddd; box-sizing: border-box; margin: 0 auto;">
#               <div style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee;">
#                 <img src="{logo_url}" alt="Ascencia Logo" style="height: 70px; margin-bottom: 10px;">
#               </div>
#               <img src="https://ascencia-interview.com/static/img/email_template_icon/interviewcomplete.png" alt="Interview Submitted" style="width: 50%; display: block; margin: 20px auto;" />
#               <h2 style="color: #2c3e50; text-align: center; line-height:1.4;">Final Reminder <br/>Complete Interview Before Deadline</h2>
#               <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <b>{student_name}</b>,</p>
#               <p style="color: #d9534f; font-size: 16px; font-weight: bold; line-height: 1.6;">
#                 ⏰ <strong>Note:</strong> The interview link will expire in 24 hours. Kindly make sure the student completes the interview before the deadline.
#               </p>
#               <p style="color: #555; font-size: 16px; line-height: 1.6;"><strong>Interview Details:</strong></p>
#               <p style="color: #555; font-size: 14px; line-height: 1.6;"><strong>Interviewer name: </strong> {student_name}</p>
#               <p style="color: #555; font-size: 14px;"><strong>Start Date and time: </strong> {formatted_start}</p>
#               <p style="color: #555; font-size: 14px;"><strong>End Date and time: </strong> {formatted_end}</p>
#               <p style="color: #555; font-size: 14px;">please note that you can only access the interview between the start and end times mentioned above.</p>
#               <div style="text-align: left; margin-top: 30px;">
#                 <a href="{interview_url}" target="_blank" style="background-color: #db2777; color: #fff; padding: 12px 25px; font-size: 16px; text-decoration: none; border-radius: 5px;">
#                  Start Interview
#                 </a>
#               </div>
#               <p style="color: #555; font-size: 16px; line-height: 1.6; margin-top: 30px;">
#                 Best regards,<br/>
#                 <strong>{company_name}</strong>
#               </p>
#             </div>
#           </body>
#         </html>
#         """

#         try:
#             print(f">>> Sending reminder to: {interview_url}")
#             email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
#             email.attach_alternative(html_content, "text/html")
#             email.send(fail_silently=False)

#             student.reminder_sent = True
#             student.save(update_fields=["reminder_sent"])
#             print(">>> Email sent successfully")
#             logger.info("Interview reminder sent to %s", interview_url)

#         except Exception as e:
#             print(">>> Email error:", e)
#             logger.error("Reminder send failed: %s", str(e))


# def schedule_reminders_for_all():
#     print(">>> schedule_reminders_for_all() triggered <<<") 
#     now_time = now()
#     expiry_threshold = now_time + timedelta(hours=24)
#     students = StudentInterviewLink.objects.filter(
#         interview_attend=False,
#         is_expired=False,
#         reminder_sent=False,
#         expires_at__lte=expiry_threshold,
#         expires_at__gte=now_time
#     )
#     if students.exists():
#         for student in students:
#             send_interview_reminders(student.zoho_lead_id)
#     else:
#         print(">>> No students found for reminders <<<")


def send_interview_reminders(zoho_lead_id, reminder_type="24h"):
    print(f">>> Running {reminder_type} reminder check <<<")
    now_time = now()

    # Choose the right timing window and flags
    if reminder_type == "24h":
        expiry_threshold = now_time + timedelta(hours=24)
        pending_students = StudentInterviewLink.objects.filter(
            zoho_lead_id=zoho_lead_id,
            interview_attend=False,
            is_expired=False,
            reminder_sent=False,
            expires_at__lte=expiry_threshold,
            expires_at__gte=now_time
        )
    elif reminder_type == "1h":
        expiry_threshold = now_time + timedelta(hours=1)
        pending_students = StudentInterviewLink.objects.filter(
            zoho_lead_id=zoho_lead_id,
            interview_attend=False,
            is_expired=False,
            reminder_1hr_sent=False,
            expires_at__lte=expiry_threshold,
            expires_at__gte=now_time
        )
    else:
        print(">>> Invalid reminder type <<<")
        return

    count = pending_students.count()
    print(f">>> Found {count} students for {reminder_type} reminder <<<")

    for student in pending_students:
        student_obj = Students.objects.filter(zoho_lead_id=student.zoho_lead_id).first()
        student_name = student_obj.first_name
        student_email = student_obj.email
        interview_url = student.interview_link
        interview_start = student.created_at
        interview_end = student.expires_at

        tz = pytz.timezone("Europe/Malta")
        formatted_start = localtime(interview_start).astimezone(tz).strftime("%d %b %Y - %I:%M %p (Europe/Malta)")
        formatted_end = localtime(interview_end).astimezone(tz).strftime("%d %b %Y - %I:%M %p (Europe/Malta)")
        # Friendly time label for email display
        reminder_display = "1 hour" if reminder_type == "1h" else "24 hours"

        student1 = Students.objects.get(zoho_lead_id=zoho_lead_id)

        crm_id = student1.crm_id
        logo_url, company_name = get_email_branding(crm_id)
        # Email content
        subject = f"Interview reminder - Expires in {reminder_display}"
        text_content = f"Reminder: Interview for {student_name} expires in {reminder_display}. Visit: {interview_url}"

        # to_email = ["vaibhav@angel-portal.com"]
        to_email = [student_email]

        # You can customize the HTML based on reminder_type

        if reminder_type == '1h':
            reminder_note = f"⏰ <strong>Note:</strong> The interview link will expire in <b>{reminder_display}</b>. Kindly make sure the student completes the interview before the deadline."
        else:
            reminder_note = f"⏰ <strong>Note:</strong> The interview link will expire in <b>{reminder_display}</b>. Kindly make sure the student completes the interview before the deadline."


        html_content = f"""
            <html>
          <body style="background-color: #f4f4f4; font-family: Tahoma, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh;">
            <div style="background: #ffffff; max-width: 600px; width: 100%; padding: 30px 25px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border: 1px solid #ddd; box-sizing: border-box; margin: 0 auto;">
              <div style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee;">
                <img src="{logo_url}" alt="Ascencia Logo" style="height: 70px; margin-bottom: 10px;">
              </div>
              <img src="https://ascencia-interview.com/static/img/email_template_icon/interviewcomplete.png" alt="Interview Submitted" style="width: 50%; display: block; margin: 20px auto;" />
              <h2 style="color: #2c3e50; text-align: center; line-height:1.4;">Final Reminder <br/>Complete Interview Before Deadline</h2>
              <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <b>{student_name}</b>,</p>
              <p style="color: #d9534f; font-size: 16px; font-weight: bold; line-height: 1.6;">
                {reminder_note}
              </p>
              <p style="color: #555; font-size: 16px; line-height: 1.6;"><strong>Interview Details:</strong></p>
              <p style="color: #555; font-size: 14px; line-height: 1.6;"><strong>Interviewer name: </strong> {student_name}</p>

              <p style="color: #555; font-size: 14px;"><strong>Expiry Date and time: </strong> {formatted_end}</p>
              <p style="color: #555; font-size: 14px;">Please note that you can access the interview only until the expiry date and time mentioned above.</p>
              <div style="text-align: left; margin-top: 30px;">
                <a href="{interview_url}" target="_blank" style="background-color: #db2777; color: #fff; padding: 12px 25px; font-size: 16px; text-decoration: none; border-radius: 5px;">
                 Start Interview
                </a>
              </div>
              <p style="color: #555; font-size: 16px; line-height: 1.6; margin-top: 30px;">
                Best regards,<br/>
                <strong>{company_name}</strong>
              </p>
            </div>
          </body>
        </html>"""

        try:
            print(f">>> Sending {reminder_type} reminder to: {interview_url}")
            email = EmailMultiAlternatives(subject, text_content, "", to_email,cc=settings.DEFAULT_CC_EMAILS)
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            # send_email(
            #     subject=subject,
            #     message=html_content,
            #     recipient=to_email
            # )


            if reminder_type == "24h":
                student.reminder_sent = True
                student.save(update_fields=["reminder_sent"])
            elif reminder_type == "1h":
                student.reminder_1hr_sent = True
                student.save(update_fields=["reminder_1hr_sent"])

            print(">>> Email sent successfully")
            logger.info(f"{reminder_type} reminder sent to %s", interview_url)

        except Exception as e:
            print(">>> Email error:", e)
            logger.error("Reminder send failed: %s", str(e))


def schedule_reminders_for_all():
    print(">>> schedule_reminders_for_all() triggered <<<") 
    now_time = now()

    # 24-hour reminder check
    students_24h = StudentInterviewLink.objects.filter(
        interview_attend=False,
        is_expired=False,
        reminder_sent=False,
        expires_at__lte=now_time + timedelta(hours=24),
        expires_at__gte=now_time
    )
    for student in students_24h:
        send_interview_reminders(student.zoho_lead_id, reminder_type="24h")

    # 1-hour reminder check
    students_1h = StudentInterviewLink.objects.filter(
        interview_attend=False,
        is_expired=False,
        reminder_1hr_sent=False,
        expires_at__lte=now_time + timedelta(hours=1),
        expires_at__gte=now_time
    )
    for student in students_1h:
        send_interview_reminders(student.zoho_lead_id, reminder_type="1h")

    if not students_24h.exists() and not students_1h.exists():
        print(">>> No students found for any reminders <<<")
        