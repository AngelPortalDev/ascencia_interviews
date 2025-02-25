from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from adminpanel.models.institute import Institute 

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class StudentManagerProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,  
        related_name='student_manager_profile'
    )
    institute_id = models.ForeignKey(
        Institute, 
        on_delete=models.CASCADE, 
        related_name='student_manager_profile'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    
    class Meta:
        indexes = [
            models.Index(fields=['institute_id']),
        ]
        verbose_name = "StudentManagerProfile"
        verbose_name_plural = "StudentManagerProfile"
   
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    
    objects = models.Manager() 
    active_objects = ActiveManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
