from django.db import models
from django.utils.timezone import now

class ZohoToken(models.Model):
    crm_name = models.CharField(max_length=100, unique=True,null=True,)  
    access_token = models.CharField(max_length=500)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_expired(self):
        # print(f"now: {now()}, expires_at: {self.expires_at}")
        return now() >= self.expires_at

    def __str__(self):
        return f"{self.crm_name} - Expires at {self.expires_at}"