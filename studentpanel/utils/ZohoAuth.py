import requests
import json
from django.conf import settings
from django.core.cache import cache

# class ZohoAuth:
#     ZOHO_CLIENT_ID = "1000.7ED8CAF9C95QVFKAFORL6ZI3D6SQCS"
#     ZOHO_CLIENT_SECRET = "bdffd3ef1302e199b24edcd0017115733af5927b52"
#     ZOHO_REFRESH_TOKEN = "1000.6e8e4e04b17ef7515d974e3e24fb2579.6757812a7accb6f428db9cf0f6d8d9c2"
#     ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
    
#     @classmethod
#     def get_access_token(cls):
#         access_token = cache.get("zoho_access_token")
#         if access_token:
#             return access_token

#         data = {
#             "client_id": cls.ZOHO_CLIENT_ID,
#             "client_secret": cls.ZOHO_CLIENT_SECRET,
#             "refresh_token": cls.ZOHO_REFRESH_TOKEN,
#             "grant_type": "refresh_token"
#         }

#         response = requests.post(cls.ZOHO_TOKEN_URL, data=data)
        
#         if response.status_code == 200:
#             access_token = response.json().get("access_token")
#             cache.set("zoho_access_token", access_token, timeout=55 * 60)
#             print(f"Zoho Token Fetch Passed: {response.text}")
#             return access_token
#         else:
#             print(f"Zoho Token Fetch Failed: {response.text}")
#             raise Exception(f"Zoho Token Fetch Failed: {response.text}")





class ZohoAuth:
    # Store credentials mapped to Zoho CRM IDs
    ZOHO_CREDENTIALS = {
        "771809603": {  # Ascencia Malta
            "client_id": "1000.7ED8CAF9C95QVFKAFORL6ZI3D6SQCS",  
            "client_secret": "bdffd3ef1302e199b24edcd0017115733af5927b52",  
            "refresh_token": "1000.6e8e4e04b17ef7515d974e3e24fb2579.6757812a7accb6f428db9cf0f6d8d9c2"  
        }
    }

    ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"


    @classmethod
    def get_access_token(cls, crm_id):
        """Fetch Zoho access token with caching and retry mechanism (without throttling)."""
        
        if crm_id not in cls.ZOHO_CREDENTIALS:
            raise ValueError(f"Invalid Zoho CRM ID: {crm_id}")

        cache_key = f"zoho_access_token_{crm_id}"
        access_token = cache.get(cache_key)

        # ✅ Return cached token if available
        if access_token:
            return access_token

        creds = cls.ZOHO_CREDENTIALS[crm_id]
        data = {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token"
        }

        max_retries = 5  # ✅ Limit retries to prevent overloading Zoho API
        delay = 5  # Initial retry delay (in seconds)

        for attempt in range(max_retries):
            response = requests.post(cls.ZOHO_TOKEN_URL, data=data)
            response_json = response.json()

            if response.status_code == 200 and "access_token" in response_json:
                access_token = response_json["access_token"]
                
                # ✅ Cache the token for ~55 minutes
                cache.set(cache_key, access_token, timeout=55 * 60)

                print(f"✅ Zoho Token Fetch Passed for CRM {crm_id}")
                return access_token

            elif response_json.get("error") == "access_denied":
                print(f"⏳ Too many requests to Zoho API. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # ✅ Exponential Backoff (5s, 10s, 20s...)
            else:
                print(f"❌ Zoho Token Fetch Failed for CRM {crm_id}: {response.text}")
                break  # Stop retrying if it's another error

        raise Exception(f"Zoho Token Fetch Failed for CRM {crm_id} after {max_retries} attempts.")




    # @classmethod
    # def get_access_token(cls, crm_id):
        if crm_id not in cls.ZOHO_CREDENTIALS:
            raise ValueError(f"Invalid Zoho CRM ID: {crm_id}")

        cache_key = f"zoho_access_token_{crm_id}"
        access_token = cache.get(cache_key)
        if access_token:
            return access_token  # Return cached token

        creds = cls.ZOHO_CREDENTIALS[crm_id]

        data = {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token"
        }

        response = requests.post(cls.ZOHO_TOKEN_URL, data=data)

        if response.status_code == 200:
            access_token = response.json().get("access_token")
            cache.set(cache_key, access_token, timeout=55 * 60)  # Store for 55 minutes
            print(f"Zoho Token Fetch Passed for CRM {crm_id}: {response.text}")
            return access_token
        else:
            print(f"Zoho Token Fetch Failed for CRM {crm_id}: {response.text}")
            raise Exception(f"Zoho Token Fetch Failed for CRM {crm_id}: {response.text}")