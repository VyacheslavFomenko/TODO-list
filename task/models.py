from django.contrib.contenttypes.models import ContentType
from django.db import models

from user.models import User


class Status(models.Model):
    name = models.CharField(max_length=255, unique=True)
    editable = models.BooleanField(default=False)


class FileImage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    doc = models.ImageField(upload_to='uploads/')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name="task")
    assigned_to = models.ManyToManyField(User, related_name="task")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
