from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from adminpanel.models.institute import Institute  


class ActiveManager(models.Manager):
    """Custom manager to filter out soft-deleted records."""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Course(models.Model):
    course_name = models.CharField(max_length=255)
    crm_id = models.ForeignKey(
        Institute, 
        on_delete=models.CASCADE, 
        related_name='courses'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['crm_id']),
        ]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def soft_delete(self):
        """Soft delete the course by setting the deleted_at field."""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore the course by clearing the deleted_at field."""
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        """Check if the course is soft deleted."""

        return self.deleted_at is not None

    def __str__(self):
        return self.course_name

    # Managers
    objects = models.Manager()  # Default manager for all records
    active_objects = ActiveManager()  # Custom manager for non-deleted records

    def save(self, *args, **kwargs):
        """Override save to ensure the integrity of the deleted_at field."""
        if self.deleted_at and 'update_fields' in kwargs and 'deleted_at' not in kwargs['update_fields']:
            raise ValueError("Cannot modify a soft-deleted record without updating 'deleted_at'.")
        super().save(*args, **kwargs)
