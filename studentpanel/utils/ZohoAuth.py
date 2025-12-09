import requests
import json
from django.conf import settings
from django.core.cache import cache
from studentpanel.models.zoho_access_token import ZohoToken
from django.utils.timezone import now, timedelta
import time


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
        },
        "771661420":{  #india
            "client_id": "1000.B9BWXZLVKXOM71BCVWF3K1MSU0FIJX",
            "client_secret": "b236e7008315921814ad4fcc480374361b968eb4e0",
            "refresh_token": "1000.59874d22ad5569d7c5efd49774bc48a8.f98660728b67e62704ba193733b87023"
        },
        "755071407":{   #cdp india
             "client_id": "1000.DF90S3HTTPHIX1D42TR3PTCOZAXM6U",
            "client_secret": "85ecb536123ed7e3201251468c5ae6a7fcd7556ba4",
            "refresh_token": "1000.0decc57b59c3102e0aa39649c460aad7.30b8851b125f0473917f119db6df9545"
        },
        "759439531":{ #cdp intl
            "client_id": "1000.IZUYAE9LTARMXSSDT8KCCLE50WTFMJ",
            "client_secret": "3aeba7803c708b930397b086f608ae0bc3ee8a5d80",
            "refresh_token": "1000.04ce2010702b45902a849b84c592b50d.eda54262af42f40d304130776f57bb12"
        }
    }

    ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"


    @classmethod
    def get_access_token(cls, crm_id):
        """
        Get Zoho access token from cache, DB, or refresh if expired.
        """
        if crm_id not in cls.ZOHO_CREDENTIALS:
            raise ValueError(f"Invalid Zoho CRM ID: {crm_id}")

        cache_key = f"zoho_access_token_{crm_id}"
        access_token = cache.get(cache_key)
        if access_token:
            return access_token

        # Try DB
        token_record = ZohoToken.objects.filter(crm_name=crm_id).first()
        if token_record and token_record.expires_at > now():
            cache.set(cache_key, token_record.access_token, timeout=55 * 60)
            return token_record.access_token

        # Otherwise, refresh token
        access_token = cls.refresh_access_token(crm_id)
        cache.set(cache_key, access_token, timeout=55 * 60)
        return access_token

    @classmethod
    def refresh_access_token(cls, crm_id):
        """
        Refresh Zoho access token using CRM credentials and store in DB.
        Retries on temporary failures using exponential backoff.
        """
        creds = cls.ZOHO_CREDENTIALS.get(crm_id)
        if not creds:
            raise Exception(f"CRM {crm_id} not found in credentials!")

        data = {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token"
        }

        max_retries = 5
        delay = 5

        for attempt in range(max_retries):
            try:
                response = requests.post(cls.ZOHO_TOKEN_URL, data=data, timeout=10)
                resp_json = response.json()

                if response.status_code == 200 and "access_token" in resp_json:
                    access_token = resp_json["access_token"]
                    expires_at = now() + timedelta(minutes=55)

                    # Save or update token in DB
                    ZohoToken.objects.update_or_create(
                        crm_name=crm_id,
                        defaults={"access_token": access_token, "expires_at": expires_at}
                    )
                    print(f"✅ Zoho Token refreshed for CRM {crm_id}")
                    return access_token

                elif resp_json.get("error") == "access_denied":
                    print(f"⏳ Too many requests to Zoho API. Retrying in {delay} sec...")
                    time.sleep(delay)
                    delay *= 2  # exponential backoff

                else:
                    print(f"❌ Zoho Token fetch failed for CRM {crm_id}: {response.text}")
                    break

            except requests.RequestException as e:
                print(f"⚠️ Request error: {str(e)}. Retrying in {delay} sec...")
                time.sleep(delay)
                delay *= 2

        raise Exception(f"Failed to fetch Zoho token for CRM {crm_id} after {max_retries} attempts")


    # @classmethod
    # def get_access_token(cls, crm_id):
    #     """Fetch Zoho access token with caching and retry mechanism (without throttling)."""
        
    #     if crm_id not in cls.ZOHO_CREDENTIALS:
    #         raise ValueError(f"Invalid Zoho CRM ID: {crm_id}")

    #     cache_key = f"zoho_access_token_{crm_id}"
    #     access_token = cache.get(cache_key)

    #     # ✅ Return cached token if available
    #     if access_token:
    #         return access_token

    #     creds = cls.ZOHO_CREDENTIALS[crm_id]
    #     data = {
    #         "client_id": creds["client_id"],
    #         "client_secret": creds["client_secret"],
    #         "refresh_token": creds["refresh_token"],
    #         "grant_type": "refresh_token"
    #     }

    #     max_retries = 5  # ✅ Limit retries to prevent overloading Zoho API
    #     delay = 5  # Initial retry delay (in seconds)

    #     for attempt in range(max_retries):
    #         response = requests.post(cls.ZOHO_TOKEN_URL, data=data)
    #         response_json = response.json()

    #         if response.status_code == 200 and "access_token" in response_json:
    #             access_token = response_json["access_token"]
                
    #             # ✅ Cache the token for ~55 minutes
    #             cache.set(cache_key, access_token, timeout=55 * 60)

    #             print(f"✅ Zoho Token Fetch Passed for CRM {crm_id}")
    #             return access_token

    #         elif response_json.get("error") == "access_denied":
    #             print(f"⏳ Too many requests to Zoho API. Retrying in {delay} seconds...")
    #             time.sleep(delay)
    #             delay *= 2  # ✅ Exponential Backoff (5s, 10s, 20s...)
    #         else:
    #             print(f"❌ Zoho Token Fetch Failed for CRM {crm_id}: {response.text}")
    #             break  # Stop retrying if it's another error

    #     raise Exception(f"Zoho Token Fetch Failed for CRM {crm_id} after {max_retries} attempts.")




    # @classmethod
    # def get_access_token(cls, crm_id):
        # if crm_id not in cls.ZOHO_CREDENTIALS:
        #     raise ValueError(f"Invalid Zoho CRM ID: {crm_id}")

        # cache_key = f"zoho_access_token_{crm_id}"
        # access_token = cache.get(cache_key)
        # if access_token:
        #     return access_token  # Return cached token

        # creds = cls.ZOHO_CREDENTIALS[crm_id]

        # data = {
        #     "client_id": creds["client_id"],
        #     "client_secret": creds["client_secret"],
        #     "refresh_token": creds["refresh_token"],
        #     "grant_type": "refresh_token"
        # }

        # response = requests.post(cls.ZOHO_TOKEN_URL, data=data)

        # if response.status_code == 200:
        #     access_token = response.json().get("access_token")
        #     cache.set(cache_key, access_token, timeout=55 * 60)  # Store for 55 minutes
        #     print(f"Zoho Token Fetch Passed for CRM {crm_id}: {response.text}")
        #     return access_token
        # else:
        #     print(f"Zoho Token Fetch Failed for CRM {crm_id}: {response.text}")
        #     raise Exception(f"Zoho Token Fetch Failed for CRM {crm_id}: {response.text}")