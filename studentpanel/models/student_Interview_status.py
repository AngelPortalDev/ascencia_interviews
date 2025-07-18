from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now  # Import Django's timezone utility
from studentpanel.models.interview_process_model import Students
import uuid  # Import UUID
from django.conf import settings


class Student_Interview(models.Model):
    # student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    zoho_lead_id = models.CharField(max_length=100,null=False)
    interview_process = models.CharField(max_length=225,null=True,blank=True)
    profile_photo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]
        verbose_name = "Student_status"
        verbose_name_plural = "Student_status"

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

        # objects = models.Manager()
        # active_objects = ActiveManager()

    
    # def save(self, *args, **kwargs):
    #     """Override save to ensure the integrity of the deleted_at field."""
    #     if self.deleted_at and 'update_fields' in kwargs and 'deleted_at' not in kwargs['update_fields']:
    #         raise ValueError("Cannot modify a soft-deleted record without updating 'deleted_at'.")

    #     domain = getattr(settings, "SITE_DOMAIN", f"{settings.ADMIN_BASE_URL}")
    #     self.interview_link = f"{domain}/interview/{self.interview_id}"

    #     super().save(*args, **kwargs)

