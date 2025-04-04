from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now  # Import Django's timezone utility
from adminpanel.models.institute import Institute  



class Students(models.Model):

    STATUS_CHOICES = [
        ('unverified', 'Unverified'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    student_id = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=225)
    email = models.EmailField(max_length=225, unique=True, blank=False)
    student_manager_email = models.EmailField(max_length=225, null=True, blank=False)
    phone = models.CharField(max_length=20, null=True)  # Use CharField to handle leading zeros
    dob = models.DateField(null=True)  # Date of Birth field 
    program = models.CharField(max_length=100, null=True, blank=True)
    intake_year = models.CharField(max_length=100, null=True, blank=True)
    intake_month = models.CharField(max_length=100, null=True, blank=True)
    zoho_lead_id = models.CharField(max_length=100, unique=True, null=False)
    crm_id = models.CharField(max_length=225, null=True, blank=False)
    # institute_id = models.ForeignKey(
    #     Institute, 
    #     on_delete=models.CASCADE, 
    #     related_name='students', null=True, blank=True
    # )
    edu_doc_verification_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Unverified'
    )
    mindee_verification_status = models.CharField(
        max_length=20, 
        default='',
        blank=True, 
        null=True
    )
    verification_failed_reason = models.TextField(null=True, blank=True)
    is_interview_link_sent = models.BooleanField(default=False)
    interview_link_send_count = models.IntegerField(default=0)
    bunny_stream_video_id = models.CharField(max_length=255, null=True, blank=True)
    student_consent = models.IntegerField(blank=False, null=True)  # You might want to validate this with choices
    interview_start_at = models.DateTimeField(auto_now=False, blank=False, null=True)
    answers_scores = models.IntegerField(blank=False, null=True)
    sentiment_score = models.IntegerField(blank=False, null=True)
    recording_file = models.TextField(blank=False, null=True)
    interview_end_at = models.DateTimeField(auto_now=False, blank=False, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=now)  # Instead of auto_now_add=True
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]
        verbose_name = "Student"
        verbose_name_plural = "Students"

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