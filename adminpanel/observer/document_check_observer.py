# adminpanel/observer.py
import requests
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from studentpanel.models.interview_process_model import Students
from urllib.parse import quote
from studentpanel.utils.ZohoAuth import ZohoAuth

# API Data Fetcher (Observer)
class APIDataFetcher:
    """Observer that fetches data from the Zoho API when notified"""
    
    def notify(self, publisher):
        # print(r'first_name:', publisher.first_name)
        # print(r'last_name:', publisher.last_name)
        API_URL = f"https://www.zohoapis.com/crm/v2/Leads/{publisher.zoho_lead_id}/Attachments"
        # API_TOKEN = "1000.8b4ec0922ee977f16a8b5629ad27b194.e57d64ff95fcb9257010a219b9a972f7"  # Store token securely
        API_TOKEN = ZohoAuth.get_access_token()

        print(r'API_TOKEN:', API_TOKEN)
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(API_URL, headers=headers)
            response.raise_for_status()  # Raises an error for bad responses
            data = response.json()
            # print(f"✅ API Response: {data}")  # Print API data
            count = len(data['data'])
            # print(f"🔢 Count of Data: {count}")
            for item in data['data']:
                file_id = item['$file_id']
                parent_id = item['Parent_Id']['id']
                file_name = item['File_Name']
                
                encoded_file_name = quote(file_name)

                # Construct the URL dynamically
                file_url  = f"https://crm.zoho.com/crm/org771809603/ViewAttachment?fileId={file_id}&module=Leads&parentId={parent_id}&creatorId=null&id={item['id']}&name={encoded_file_name}&downLoadMode=pdfViewPlugin"

                # print(f"🔗 Document URL: {file_url }")

                file_response = requests.get(file_url)
                program = publisher.program if publisher.program else ''
                first_name = publisher.first_name if publisher.first_name else ''
                last_name = publisher.last_name if publisher.last_name else ''
                zoho_lead_id = publisher.zoho_lead_id if publisher.zoho_lead_id else ''

                if file_response.status_code == 200:

                    process_api_url = "http://127.0.0.1:8000/api/process_document"
                    files = {"document": (file_url, file_response.content, "application/pdf")}
                    data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "program": program,
                        "zoho_lead_id": zoho_lead_id,
                        "API_TOKEN": API_TOKEN,
                    }

                    process_response = requests.post(process_api_url, files=files, data=data)
                    print(process_response.json())
                else:
                    print("Failed to download file")

        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")

    # Signal Handler (Observer Trigger)
    # @receiver(post_save, sender=Students)
    # def student_created_observer(sender, instance, created, **kwargs):
    #     if created:  # Ensure it's triggered only on creation, not updates
    #         print(f"A new student was created: {instance}")
            
    #         # Create the observer instance
    #         api_observer = APIDataFetcher()
            
    #         # Trigger the observer to fetch API data
    #         api_observer.notify(instance)

    #     else:
    #         print(f"A new student was updated: {instance}")
    #         # Create the observer instance
    #         api_observer = APIDataFetcher()
            
    #         # Trigger the observer to fetch API data
    #         api_observer.notify(instance)


    @receiver(post_save, sender=Students)
    def student_created_observer(sender, instance, created, **kwargs):
        if created:
            print(f"A new student was created: {instance}")
        else:
            print(f"A student was updated: {instance}")

        # Create the observer instance
        api_observer = APIDataFetcher()

        # Check conditions before calling notify
        if instance.edu_doc_verification_status == 'Unverified' or (
            instance.edu_doc_verification_status == 'rejected' and instance.interview_link_send_count < 2
        ):
            # Trigger API fetch only if conditions match
            api_observer.notify(instance)
