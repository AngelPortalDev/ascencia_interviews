from django.db import models

class Lead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    zoho_lead_id = models.TextField()  # Fixed the field name
    passport = models.FileField(upload_to='passport_uploads/')  # Corrected the field name and added upload_to path
    updated = models.DateTimeField(auto_now=True)  # Changed to auto_now for updates
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
