# adminpanel/observer.py
import requests
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from studentpanel.models.interview_process_model import Students
from urllib.parse import quote
from studentpanel.utils.ZohoAuth import ZohoAuth
import time
import threading
from queue import Queue
from django.conf import settings
from django_q.tasks import async_task



process_queue = Queue()
lock = threading.Lock()


class APIDataFetcher:
    def notify(self, publisher):

        API_URL = f"https://www.zohoapis.com/crm/v2/Leads/{publisher.zoho_lead_id}/Attachments"

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
            count = len(data['data'])

            for item in data['data']:
                file_id = item['$file_id']
                parent_id = item['Parent_Id']['id']
                file_name = item['File_Name']
                encoded_file_name = quote(file_name)

                file_url = (
                    f"https://crm.zoho.com/crm/org771809603/ViewAttachment?"
                    f"fileId={file_id}&module=Leads&parentId={parent_id}&id={item['id']}"
                    f"&name={encoded_file_name}&downLoadMode=pdfViewPlugin"
                )

                # process_queue.put((file_url, publisher, API_TOKEN))
                # process_documents()
                # if zoho_lead_id in ['5204268000112707003', '5204268000116210079']:
                async_task("adminpanel.observer.document_check_observer.process_documents_task", file_url, publisher, API_TOKEN)


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



def process_documents_task(file_url, publisher, API_TOKEN):
    """Processes a single document in a Django Q worker."""
    import requests
    import time
    from django.conf import settings

    # Fetch document
    file_response = requests.get(file_url)
    if file_response.status_code != 200:
        print(f"❌ Failed to download file: {file_url}")
        return

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
    files = {"document": (file_url, file_response.content, "application/pdf")}

    try:
        process_response = requests.post(process_api_url, files=files, data=data)
        print(f"✅ Document processed: {process_response.json()}")
    except requests.RequestException as e:
        print(f"❌ Processing failed: {e}")

    time.sleep(5)  # Optional delay



@receiver(post_save, sender=Students)
def student_created_observer(sender, instance, created, **kwargs):
    if created:
        print(f"A new student was created: {instance}")
    else:
        print(f"A student was updated: {instance}")

    api_observer = APIDataFetcher()

    if instance.edu_doc_verification_status == 'Unverified' or (
        instance.edu_doc_verification_status == 'rejected' and instance.interview_link_send_count < 2
    ):
        api_observer.notify(instance) 
