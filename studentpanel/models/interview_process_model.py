from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Students(models.Model):
    student_id = models.IntegerField()
    first_name = models.CharField(max_length=255,null=True)
    last_name = models.CharField(max_length=225,null=True)
    email = models.EmailField(max_length=225,null=True)
    phone = models.CharField(max_length=20,null=True)  # Use CharField to handle leading zeros
    dob = models.DateField(null=True, blank=True)  # Date of Birth field 
    student_consent = models.IntegerField()
    interview_start_at = models.DateTimeField(auto_now=True)
    answers_scores = models.IntegerField()
    sentiment_score = models.IntegerField()
    recording_file = models.TextField()
    interview_end_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


    class Meta:
       indexes = [
            models.Index(fields=['id']),
        ]
        # verbose_name = "InterviewData"
        # verbose_name_plural = "InterviewData"

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