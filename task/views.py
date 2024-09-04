from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from task.models import FileImage, Task, Status
from task.serializers import TaskSerializer, StatusSerializer

from django.contrib.contenttypes.models import ContentType


# Create your views here.


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    image_serializer_class = FileImage

    def get_serializer_class(self):
        if self.action == "add_image":
            return self.image_serializer_class
        return super().get_serializer_class()

    @action(details=True, mathods=["POST"])
    def add_image(self, request, pk):
        data = request.data
        data["content_type"] = ContentType.objects.get_for_model(Task)
        data["object_id"] = pk
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        return serializer.data


class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer
    queryset = Status.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name_icontains=name)
        return queryset.distinct()
