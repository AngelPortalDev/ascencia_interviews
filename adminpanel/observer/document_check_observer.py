# adminpanel/observer.py
import requests
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from studentpanel.models.interview_process_model import Students

# API Data Fetcher (Observer)
class APIDataFetcher:
    """Observer that fetches data from the Zoho API when notified"""
    
    def notify(self, publisher):
        API_URL = "https://www.zohoapis.com/crm/v2/Leads/5204268000108826399/Attachments"
        API_TOKEN = "1000.3df4657ba64598cab2813479f282c0b4.0990acdfb226a4b8b77b4e0eba0894b6"  # Store token securely

        print(f"🌐 Fetching API data for: {publisher.first_name}...")

        headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(self.API_URL, headers=headers)
            response.raise_for_status()  # Raises an error for bad responses
            data = response.json()
            print(f"✅ API Response: {data}")  # Print API data

        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")

# Signal Handler (Observer Trigger)
@receiver(post_save, sender=Students)
def student_created_observer(sender, instance, created, **kwargs):
    """
    Triggered when a new student is created.
    """
    if created:  # Ensure it's triggered only on creation, not updates
        print(f"A new student was created: {instance.first_name}")
        
        # Create the observer instance
        api_observer = APIDataFetcher()
        
        # Trigger the observer to fetch API data
        api_observer.notify(instance)
