import requests
import json
from django.conf import settings
from django.core.cache import cache

class ZohoAuth:
    ZOHO_CLIENT_ID = "1000.7ED8CAF9C95QVFKAFORL6ZI3D6SQCS"
    ZOHO_CLIENT_SECRET = "bdffd3ef1302e199b24edcd0017115733af5927b52"
    ZOHO_REFRESH_TOKEN = "1000.6e8e4e04b17ef7515d974e3e24fb2579.6757812a7accb6f428db9cf0f6d8d9c2"
    ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
    
    @classmethod
    def get_access_token(cls):
        access_token = cache.get("zoho_access_token")
        if access_token:
            return access_token

        data = {
            "client_id": cls.ZOHO_CLIENT_ID,
            "client_secret": cls.ZOHO_CLIENT_SECRET,
            "refresh_token": cls.ZOHO_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }

        response = requests.post(cls.ZOHO_TOKEN_URL, data=data)
        
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            cache.set("zoho_access_token", access_token, timeout=55 * 60)
            print(f"Zoho Token Fetch Passed: {response.text}")
            return access_token
        else:
            print(f"Zoho Token Fetch Failed: {response.text}")
            raise Exception(f"Zoho Token Fetch Failed: {response.text}")
