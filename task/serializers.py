from rest_framework import serializers

from task.models import FileImage, Task, Status
from django.contrib.contenttypes.models import ContentType


class FileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileImage
        fields = ("id", "content_type", "object_id", "doc")


class TaskSerializer(serializers.ModelSerializer):
    image_files = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "assigned_to", "created_at", "updated_at", "image_files")

    def get_image_files(self, obj):
        qs = FileImage.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(Task))
        return FileImageSerializer(qs, many=True).data


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ("id", "name")
