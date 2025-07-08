from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from enum import Enum
def default_expiry():
    """Returns the default expiration time (48 hours from now)."""
    return now() + timedelta(hours=72)

class InterviewResult(Enum):
    PASS = "Pass"
    FAIL = "Fail"
    
class StudentInterviewLink(models.Model):
    zoho_lead_id = models.CharField(max_length=255, help_text="Unique identifier from Zoho CRM")
    interview_link = models.URLField(help_text="Interview link for the student")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the link was generated")
    expires_at = models.DateTimeField(default=default_expiry, help_text="Expiration timestamp (48 hours after creation)")
    interview_attend = models.BooleanField(default=False, help_text="Indicates if the student attended the interview")
    is_expired = models.BooleanField(default=False, help_text="Marks whether the link is expired")
    total_sentiment_score = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    total_answer_scores = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    total_grammar_scores = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    overall_score = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    interview_status = models.CharField(
        max_length=10, 
        choices=[(tag.value, tag.value) for tag in InterviewResult], 
        null=True
    )
    interview_link_count = models.CharField(max_length=50,null=True,blank=True)
    assigned_question_ids = models.CharField(
    max_length=255,
    null=True,
    blank=True,
    help_text="Comma-separated IDs of assigned CommonQuestion rows"
)
    transcript_text = models.TextField(null=True, blank=True, help_text="Transcript of the merged interview video")
    def save(self, *args, **kwargs):
        """Ensure expiration logic is applied before saving."""
        if self.expires_at <= now():
            self.is_expired = True
        if self.overall_score is not None:
            self.interview_status = InterviewResult.PASS.value if self.overall_score >= 35 else InterviewResult.FAIL.value
        super().save(*args, **kwargs)

    def get_result(self):
        return InterviewResult.PASS if self.interview_status == "Pass" else InterviewResult.FAIL

    def __str__(self):
        return f"{self.zoho_lead_id} - {'Expired' if self.is_expired else 'Active'}"
