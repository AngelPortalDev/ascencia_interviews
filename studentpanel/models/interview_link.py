from django.db import models
from django.utils.timezone import now
from datetime import timedelta

def default_expiry():
    """Returns the default expiration time (48 hours from now)."""
    return now() + timedelta(hours=72)

class StudentInterviewLink(models.Model):
    zoho_lead_id = models.CharField(max_length=255, help_text="Unique identifier from Zoho CRM")
    interview_link = models.URLField(help_text="Interview link for the student")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the link was generated")
    expires_at = models.DateTimeField(default=default_expiry, help_text="Expiration timestamp (48 hours after creation)")
    interview_attend = models.BooleanField(default=False, help_text="Indicates if the student attended the interview")
    is_expired = models.BooleanField(default=False, help_text="Marks whether the link is expired")

    def save(self, *args, **kwargs):
        """Ensure expiration logic is applied before saving."""
        if self.expires_at <= now():
            self.is_expired = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.zoho_lead_id} - {'Expired' if self.is_expired else 'Active'}"
