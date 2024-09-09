from rest_framework import serializers
from task.models import FileImage, Task, Status
from django.contrib.contenttypes.models import ContentType
from task.tasks import send_email_task
from todo_list.settings import DEFAULT_FROM_EMAIL

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
        source="assigned_to",
        read_only=True
    )

    class Meta:
        model = Task
        fields = (
            "id", "title", "description", "status", "status_detailed", "assigned_to", "assigned_to_detailed",
            "created_at", "updated_at", "image_files")

    def create(self, validated_data):
        task = super().create(validated_data=validated_data)
        if task:
            title_data = task.title
            description_data = task.description
            assigned_to = task.assigned_to.values_list("email", flat=True)

            for assignee in assigned_to:
                send_email_task.delay(subject=title_data, message=description_data, email_from=DEFAULT_FROM_EMAIL,
                                      recipient_list=assignee)
        return task

    def get_image_files(self, obj):
        qs = FileImage.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(Task))
        return FileImageSerializer(qs, many=True).data
