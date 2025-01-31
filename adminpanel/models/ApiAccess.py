from django.db import models


class ApiAccess(models.Model):
    access_name = models.CharField(max_length=225)
    api_key = modeels.CharField(max_length=225)
    created_by = models.IntegerField(max_length=11)
    created_at = models.DateTimeField(auto_now=true)
    update_at = models.DateTimeField(auto_now=true)
    deleted_at = models.DateTimeField(auto_now=true)
