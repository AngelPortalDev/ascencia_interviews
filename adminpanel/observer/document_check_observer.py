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
        API_URL = "https://www.zohoapis.com/crm/v2/Leads/5204268000107680064/Attachments"
        API_TOKEN = "1000.de9c1a63f860e3e76d9ee5bca3d6e898.26f08982f3a3165660f83079a78b630d"  # Store token securely

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
