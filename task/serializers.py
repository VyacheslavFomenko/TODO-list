from rest_framework import serializers
from task.models import FileImage, Task, Status
from django.contrib.contenttypes.models import ContentType
from task.tasks import send_email_task

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

    def create(self, validated_data):
        if validated_data:
            title_data = validated_data.get("title")
            description_data = validated_data.get("description")
            assigned_to = validated_data.get("assigned_to_detailed")

            for assignee in assigned_to:
                assignee_email = assignee.get("email")
                send_email_task.delay(subject=title_data, message=description_data, recipient_list=assignee_email)
