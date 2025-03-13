from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now  # Import Django's timezone utility
from studentpanel.models.interview_process_model import Students
import uuid  # Import UUID
from django.conf import settings


class Student_Interview(models.Model):
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    interview_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    interview_link = models.URLField(blank=True)
    video_response = models.FileField(upload_to="interviews/", null=True, blank=True)
    transcript = models.TextField(blank=True, null=True)
    sentiment_score = models.FloatField(null=True)
    ai_scores = models.FloatField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=now)  # Instead of auto_now_add=True
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]
        verbose_name = "Student_Interview"
        verbose_name_plural = "Student_Interview"

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
            return str(self.id)

        objects = models.Manager()
        active_objects = ActiveManager()

    
    def save(self, *args, **kwargs):
        """Override save to ensure the integrity of the deleted_at field."""
        if self.deleted_at and 'update_fields' in kwargs and 'deleted_at' not in kwargs['update_fields']:
            raise ValueError("Cannot modify a soft-deleted record without updating 'deleted_at'.")

        domain = getattr(settings, "SITE_DOMAIN", f"{settings.ADMIN_BASE_URL}")
        self.interview_link = f"{domain}/interview/{self.interview_id}"

        super().save(*args, **kwargs)

