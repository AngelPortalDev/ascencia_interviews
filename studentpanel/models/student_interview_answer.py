from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now  # Import Django's timezone utility
from adminpanel.models.institute import Institute  



class StudentInterviewAnswers(models.Model):
    
    student_id = models.CharField(max_length=100, null=True,)
    zoho_lead_id = models.CharField(max_length=100,null=False)
    question_id = models.IntegerField(blank=False, null=True)
    answer_text = models.TextField(blank=False, null=True)
    sentiment_score = models.TextField(blank=False, null=True)
    sent_subj = models.TextField(blank=False, null=True)
    grammar_accuracy=models.TextField(blank=False, null=True)
    confidence_level=models.TextField(blank=False, null=True)
    interview_end_at = models.DateTimeField(auto_now=False, blank=False, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=now)  # Instead of auto_now_add=True
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    video_path = models.TextField(blank=False, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]
        verbose_name = "StudentInterviewAnswers"
        verbose_name_plural = "StudentInterviewAnswers"

    def soft_delete(self):
        """Soft delete the student by setting the deleted_at field."""
        self.deleted_at = timezone.now()
        self.save()
    
        def restore(self):
            """Restore the student by clearing the deleted_at field."""
            self.deleted_at = None
            self.save()


        @property
        def is_deleted(self):
            """Check if the student is soft deleted."""
            return self.deleted_at is not None

        def __str__(self):
            return str(self.student_id)

        objects = models.Manager()
        active_objects = ActiveManager()

    
    def save(self, *args, **kwargs):
        """Override save to ensure the integrity of the deleted_at field."""
        if self.deleted_at and 'update_fields' in kwargs and 'deleted_at' not in kwargs['update_fields']:
            raise ValueError("Cannot modify a soft-deleted record without updating 'deleted_at'.")
        super().save(*args, **kwargs)