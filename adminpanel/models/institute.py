from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Institute(models.Model):
    institute_name = models.CharField(max_length=255)
    institute_id = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['institute_id']),
        ]
    
    def soft_delete(self):
        """Soft delete the institute by setting the deleted_at field."""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore the institute by clearing the deleted_at field."""
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        """Check if the institute is soft deleted by inspecting the deleted_at field."""
        return self.deleted_at is not None

    def __str__(self):
        return self.institute_name

    # Default manager
    objects = models.Manager()  # This includes soft-deleted records
    active_objects = models.Manager()  # Custom manager for non-deleted records only

    def save(self, *args, **kwargs):
        """Override save to prevent overwriting deleted_at field."""
        super().save(*args, **kwargs)
