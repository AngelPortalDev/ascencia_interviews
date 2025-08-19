import json
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from adminpanel.common_imports import *
from studentpanel.models.interview_process_model import Students
from datetime import datetime
import calendar
from django.conf import settings
from studentpanel.models.interview_link import StudentInterviewLink
from django.db.models import Exists, OuterRef
from django.utils.timezone import now
from django.db.models import OuterRef, Subquery
from studentpanel.models.interview_link import StudentInterviewLink
import base64
from datetime import timedelta
from django.core.mail import send_mail 
from studentpanel.models.student_Interview_status import StudentInterview
import base64
import pytz
from django.utils.timezone import localtime
from zoneinfo import ZoneInfo

# def encode_base64(value: str) -> str:
#     """Encodes a string to base64 (URL-safe)."""
#     return base64.urlsafe_b64encode(value.encode()).decode()

import base64

def encode_base64(value) -> str:
    """Encodes a value to base64 (URL-safe)."""
    # Convert any non-string to string first
    return base64.urlsafe_b64encode(str(value).encode()).decode()

def extend_first_interview_link(zoho_lead_id):

    student = Students.objects.get(zoho_lead_id=zoho_lead_id)
    interviwelink = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id)

    try:
        student = Students.objects.get(zoho_lead_id=zoho_lead_id)
    except Students.DoesNotExist:
        print(f"❌ No student found with Zoho Lead ID: {zoho_lead_id}")
        return False
    
    if StudentInterview.objects.filter(
        zoho_lead_id=zoho_lead_id,
        Extend_interview_link="YES"
    ).exists():
        print("⚠️ Interview link already extended, skipping.")
        return False
    
    # Convert to Asia/Calcutta timezone
    

    
    # 1️⃣ Check if already processed

    # 2️⃣ Get link for given Zoho Lead ID
    student_links = StudentInterviewLink.objects.filter(zoho_lead_id=zoho_lead_id)
    # print("student_links",student_links.interview_link_count)

    if student_links.count() != 1:
        print("❌ No unique student link found.")
        return False

    link = student_links.first()

    # 3️⃣ Decode interview link count
    try:
        link_count = int(base64.b64decode(link.interview_link_count))
    except Exception as e:
        print(f"❌ Base64 decode failed: {e}")
        return False

    # 4️⃣ Validation checks
    if link_count != 1:
        print("❌ Link count is not 1")
        return False

    if link.interview_attend:
        print("❌ Interview already attended")
        return False

    if link.expires_at > now():
        print("⏳ Link is still valid, no need to extend")
        return False

    # Optional: prevent double reminders
    # if link.reminder_sent:
    #     print("📩 Reminder already sent, skipping")
    #     return False

    # 5️⃣ All checks passed → extend expiry
    link.expires_at = now() + timedelta(hours=72)
    link.is_expired = False
    link.reminder_sent = False
    link.reminder_1hr_sent= False
    link.save(update_fields=["expires_at", "is_expired", "reminder_sent","reminder_1hr_sent"])

    # 6️⃣ Mark as processed in StudentInterview
    StudentInterview.objects.filter(zoho_lead_id=zoho_lead_id).update(
        Extend_interview_link="YES"
    )
    student_zoho_lead_id= student.zoho_lead_id
    
    student_name = f"{student.first_name} {student.last_name}"
    student_email = student.email
    student_program = student.program
    encoded_zoho_lead_id = encode_base64(zoho_lead_id)
    encoded_interview_link_send_count = link.interview_link_count
    interview_url = f'{settings.ADMIN_BASE_URL}/frontend/interview_panel/{encoded_zoho_lead_id}/{encoded_interview_link_send_count}'
    interviwelink1 = StudentInterviewLink.objects.get(zoho_lead_id=zoho_lead_id)
    interview_start = interviwelink1.created_at
    interview_end = interviwelink1.expires_at
    email = student.student_manager_email.strip().lower()
    student_manager = User.objects.filter(email__iexact=email).first()
    student_manager_name = ''
    if student_manager:  
        student_manager_name = f"{student_manager.first_name} {student_manager.last_name}".strip()
        print(f"student_manager_name: {student_manager_name}")
        student_manager_email = student_manager.email
    tz = pytz.timezone("Europe/Malta")
    interview_start_local = localtime(interview_start).astimezone(tz)
    interview_end_local = localtime(interview_end).astimezone(tz)

    # Format the datetime
    formatted_start = interview_start_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")
    formatted_end = interview_end_local.strftime("%d %b %Y - %I:%M %p (Europe/Malta)")

    print("Start Date and time:", formatted_start)
    print("End Date and time:", formatted_end)
    # 7️⃣ Send notification email
    send_mail(
    subject="Interview Invitation for Student Interview",
    message="Please view this email in HTML format.",  # plain text fallback
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["vaibhav@angel-portal.com"],
    html_message=f"""
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
                        <img src="https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png" alt="Ascencia Malta" />
                    </div>
                    <img src="https://ascencia-interview.com/static/img/email_template_icon/notification.png" alt="Interview Invitation" class="email-logo" />
                    
                    <h2>Extended Interview Invitation for Student Interview {student_name},</h2>
                    
                    <p>Dear Student,</p>
                    
                    <p>We are pleased to invite you to participate in the following interview:</p>
                    
                    <p><b>Interview Details:</b></p>
                    <p><b>Interviewer name:</b> {student_name}</p>
                    <p><b>Start Date and time:</b> {formatted_start}</p>
                    <p><b>End Date and time:</b> {formatted_end}</p>
                    
                    <p>Please note that you can access the interview only between the start and end times mentioned above.</p>
                    
                    <a href="{interview_url}" class="goInterviewbtnStyle">Start Interview</a>

                    <p>Best regards,<br/>Ascencia Malta</p>
                </div>
            </body>
        </html>
    """
)
        

    send_mail(
    
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    subject="Interview Invitation Sent to Student",
                                    message="Please view this email in HTML format.",
                                    html_message=f"""
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
                                    

                                            <b>Interview Link : </b><a href="{interview_url}" target="_blank">{interview_url}</a>


                                            <p>Regards,<br/>Ascencia Malta Team</p>
                                        </div>
                                    </body>
                                    </html>
                                    """,
                                    
                                    recipient_list=["vaibhav@angel-portal.com"],  # Replace with actual student manager email
                                    
                                )


    print("✅ Interview link extended and email sent.")
    return True

@csrf_exempt  # Disable CSRF for webhooks
def students_leads_api(request):
    # print(f"data get",request.POST.get('CRM Id'))
    # return HttpResponse(f"data get {request.POST.get('CRM Id')}")
    if request.method == "POST":
        first_name = request.POST.get('First Name')
        last_name = request.POST.get('Last Name')
        email = request.POST.get('Email')
        phone = request.POST.get('Phone')
        dob = request.POST.get('DOB')
        date_object = datetime.strptime(dob, "%m-%d-%Y")
        formatted_date = date_object.strftime("%Y-%m-%d")
        student_id = request.POST.get('UserId')
        zoho_lead_id =  request.POST.get('Zoho Lead Id')
        extend_link = request.POST.get('Extend Interview Link')
        print("Zoho lead id",zoho_lead_id)
        print("extend_link",extend_link)


        if zoho_lead_id != "5204268000112707003":
            return JsonResponse({"status": False, "error": "Unauthorized Zoho Lead Id"}, status=403)
        
        
        
        
        program =  request.POST.get('Program')
        intake_year =  request.POST.get('Intake Year')
        intake_month =  request.POST.get('Intake Month')
        student_manager_email = request.POST.get('Student Manager Email')
        crm_id = request.POST.get('CRM Id')
        
        if extend_link and extend_link.lower() == "yes":
            extend_first_interview_link(zoho_lead_id)
            print("not add update as a yes")
            return JsonResponse({"status": True, "message": "Student updated successfully!"}, status=200)

        try:
            data_to_save = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'dob': formatted_date,
                'phone': phone,
                'student_id': student_id,
                'zoho_lead_id': zoho_lead_id, 
                'program': program,
                'intake_year': intake_year,
                'intake_month': intake_month,
                'student_manager_email': student_manager_email,
                'crm_id': crm_id,
            }

            where = {"zoho_lead_id": zoho_lead_id}

            result = save_data(Students, data_to_save, where)
            print(r'result:', result)
            # return HttpResponse('here')
            if result['status']:
                return JsonResponse({"status": True, "message": "Student updated successfully!"}, status=200)
            else:
                return JsonResponse({"status": False, "error": result.get('error', "Failed to update the student.")}, status=400)

        except Exception as e:
            return JsonResponse({"status": False, "error": str(e)}, status=500)

    return JsonResponse({"status": False, "error": "Invalid request method"}, status=405)



def students_list(request):
    try:

        students = Students.objects.order_by('-id').filter(deleted_at__isnull=True)
        # verified_students = students.filter(edu_doc_verification_status="approved")
        # Subquery: Get latest StudentInterviewLink ID per student
        latest_link_subquery = StudentInterviewLink.objects.filter(
            zoho_lead_id=OuterRef('zoho_lead_id'),
            interview_attend=True
        ).order_by('-id').values('id')[:1]

        # Main queryset: Annotate and order students
        verified_students = Students.objects.annotate(
            latest_interview_id=Subquery(latest_link_subquery)
        ).filter(
            latest_interview_id__isnull=False,
            deleted_at__isnull=True
        ).order_by('-latest_interview_id')  # ⬅️ Latest interview first

        # rejected_students = students.filter(edu_doc_verification_status="rejected")
        #   pending_but_link_valid
        rejected_latest_link_subquery = StudentInterviewLink.objects.filter(
            zoho_lead_id=OuterRef('zoho_lead_id')
        ).order_by('-id').values('id')[:1]

        rejected_students = Students.objects.annotate(
            has_valid_link=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    expires_at__gt=now(),
                    interview_attend=False
                )
            ),
            latest_interview_id=Subquery(rejected_latest_link_subquery)
        ).filter(
            has_valid_link=True,
            deleted_at__isnull=True
        ).order_by('-latest_interview_id')

        # unverified_students = students.filter(edu_doc_verification_status="Unverified")
        # expired_and_not_attended_students
        unverified_latest_link_subquery = StudentInterviewLink.objects.filter(
            zoho_lead_id=OuterRef('zoho_lead_id')
        ).order_by('-id').values('id')[:1]

        unverified_students = Students.objects.annotate(
            has_expired_link_without_attendance=Exists(
                StudentInterviewLink.objects.filter(
                    zoho_lead_id=OuterRef('zoho_lead_id'),
                    expires_at__lt=now(),
                    interview_attend=False
                )
            ),
            latest_interview_id=Subquery(unverified_latest_link_subquery)
        ).filter(
            has_expired_link_without_attendance=True,
            deleted_at__isnull=True
        ).order_by('-latest_interview_id')  # ⬅️ Sort by latest link ID


        intake_month = request.GET.get('intake_month', '')
        intake_year = request.GET.get('intake_year', '')
        
        # Apply filters if selected
        if intake_month and intake_year.isdigit():
            students = students.filter(intake_month=intake_month, intake_year=int(intake_year))

        # if intake_month:
        #     students = students.filter(intake_month=intake_month)
            
        # if intake_year.isdigit():
        #     intake_year = int(intake_year)

        def get_student_manager_name(email):
            user = User.objects.filter(email=email).first()
            return f"{user.first_name} {user.last_name}" if user else "N/A"

        def format_student_data(queryset):
            return [
                {
                    'id': student.student_id,
                    'first_name': getattr(student, 'first_name', '') or '',
                    'last_name': getattr(student, 'last_name', '') or '',
                    'email': getattr(student, 'email', '') or '',
                    'phone': getattr(student, 'phone', '') or '',
                    'program': getattr(student, 'program', '') or '',
                    'edu_doc_verification_status': getattr(student, 'edu_doc_verification_status', '') or '',
                    'intake_year': getattr(student, 'intake_year', '') or '',
                    'intake_month': getattr(student, 'intake_month', '') or '',
                    'zoho_lead_id': getattr(student, 'zoho_lead_id', '') or '',
                    'crm_id': getattr(student, 'crm_id', '') or '',
                    'student_manager_name': get_student_manager_name(student.student_manager_email),
                }
                for student in queryset
            ]
         
        months = list(calendar.month_name)[1:]
        years = list(range(2022, 2041))   

        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('admindashboard')},
            {"name": "Students", "url": ""},
        ]

        context = {
            'all_students': format_student_data(students),
            'verified_students': format_student_data(verified_students),
            'rejected_students': format_student_data(rejected_students),
            'unverified_students': format_student_data(unverified_students),
            "intake_months": months,
            "intake_years": years,
            "selected_intake_month": intake_month,
            "selected_intake_year": intake_year,
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
        }

        return render(request, 'student/student.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the students: {e}")
        return redirect('admindashboard')




def student_detail(request, zoho_lead_id):
    student = get_object_or_404(Students, zoho_lead_id=zoho_lead_id)
    interview_link = (
    StudentInterviewLink.objects
    .filter(zoho_lead_id=zoho_lead_id)
    .exclude(transcript_text__isnull=True)
    .exclude(transcript_text__exact="")
    .order_by("-id")
    .first()
    )

    transcript_text = interview_link.transcript_text if interview_link and interview_link.transcript_text else "Transcript not available."

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Students", "url": reverse('students_list')},
        {"name": f"{student.first_name} {student.last_name}", "url": ""}
    ]

    return render(request, "student/student_detail.html", {
        "student": student,
        "transcript_text": transcript_text,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
        "BUNNY_STREAM_LIBRARY_ID": settings.BUNNY_STREAM_LIBRARY_ID
    })