from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from task.models import FileImage, Task, Status
from task.permissions import IsAbleToEdit
from task.serializers import TaskSerializer, StatusSerializer, FileImageSerializer

from django.contrib.contenttypes.models import ContentType


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsAbleToEdit]
    image_serializer_class = FileImageSerializer

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        title = self.request.query_params.get('title')
        status = self.request.query_params.get('status')
        assigned_to = self.request.query_params.get('assigned_to')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if status:
            status_ids = self._params_to_ints(status)
            queryset = queryset.filter(ststus__id__in=status_ids)
        if assigned_to:
            assigned_to_id = self._params_to_ints(assigned_to)
            queryset = queryset.filter(assigned_to__id__in=assigned_to_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "add_image":
            return self.image_serializer_class
        return super().get_serializer_class()

    @action(methods=["POST"], detail=True)
    def add_image(self, request, pk):
        data = request.data
        data["content_type"] = ContentType.objects.get_for_model(Task).pk
        data["object_id"] = pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer
    queryset = Status.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name_icontains=name)
        return queryset.distinct()
