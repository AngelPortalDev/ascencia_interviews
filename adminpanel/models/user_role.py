from django.contrib.auth.models import User
from django.db import models

class UserRoles(models.Model):
    ROLE_CHOICES = (
        (0, 'Admin'),
        (1, 'Student Manager'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.IntegerField(choices=ROLE_CHOICES, default=1)  # Default: Student Manager

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
