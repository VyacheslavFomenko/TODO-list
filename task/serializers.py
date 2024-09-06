from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from task.models import FileImage, Task, Status
from django.contrib.contenttypes.models import ContentType

from user.serializers import UserDetailSerializer


class FileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileImage
        fields = ("id", "content_type", "object_id", "doc")


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ("id", "name", "editable")


class TaskSerializer(serializers.ModelSerializer):
    image_files = serializers.SerializerMethodField()
    status_detailed = StatusSerializer(source="status", read_only=True)
    assigned_to_detailed = UserDetailSerializer(
        many=True,
        source="assigned_to"
    )

    class Meta:
        model = Task
        fields = (
            "id", "title", "description", "status", "status_detailed", "assigned_to", "assigned_to_detailed",
            "created_at", "updated_at", "image_files")

    def get_image_files(self, obj):
        qs = FileImage.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(Task))
        return FileImageSerializer(qs, many=True).data

