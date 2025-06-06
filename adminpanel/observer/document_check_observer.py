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
            
            if data.get('data') and len(data['data']) > 0:
                highest_education_doc = data['data'][0].get('Highest_Education_Doc', [])

                if highest_education_doc: 
                    attachment_Id = data['data'][0]['Highest_Education_Doc'][0]['attachment_Id']
                    file_Id = data['data'][0]['Highest_Education_Doc'][0]['file_Id']
                    file_Name = data['data'][0]['Highest_Education_Doc'][0]['file_Name']

                    # for item in data['data']:
                        # file_id = item['$file_id']
                        # parent_id = item['Parent_Id']['id']
                        # file_name = item['File_Name']

                    encoded_file_name = quote(file_Name)

                    file_url = (
                        f"https://crm.zoho.com/crm/org{publisher.crm_id}/ViewAttachment?"
                        f"fileId={file_Id}&module=Leads&parentId={publisher.zoho_lead_id}&id={attachment_Id}"
                        f"&name={encoded_file_name}&downLoadMode=pdfViewPlugin"
                    )

                    print(r'file_url:', file_url)

                    # process_queue.put((file_url, publisher, API_TOKEN))
                    # process_documents()
                    # if zoho_lead_id in ['5204268000112707003', '5204268000116210079']:
                    if publisher.mindee_verification_status != 'Inprogress':
                        # publisher.mindee_verification_status = 'Inprogress'
                        # publisher.save(update_fields=['mindee_verification_status']) 
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


def process_documents_task(file_url, publisher, API_TOKEN):
    """Processes a single document in a Django Q worker."""
    import requests
    import time
    from django.conf import settings

    # Fetch document
    try:
        file_response = requests.get(file_url)
        file_response.raise_for_status()  # This will raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"❌ Failed to download file: {file_url}, Error: {e}")
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
        # Send the request
        process_response = requests.post(process_api_url, files=files, data=data)

        # Log the response status and content for debugging
        print(f"Response Status Code: {process_response.status_code}")
        print(f"Response Content: {process_response.text}")  # This will show the raw response body

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




@receiver(post_save, sender=Students)
def student_created_observer(sender, instance, created, **kwargs):
    if created:
        print(f"A new student was created: {instance}")
    else:
        print(f"A student was updated: {instance}")

    api_observer = APIDataFetcher()

    if instance.edu_doc_verification_status == 'Unverified' or (
        instance.edu_doc_verification_status == 'rejected' and instance.interview_link_send_count < 2 and instance.mindee_verification_status != 'Completed'
    ):
        api_observer.notify(instance) 
