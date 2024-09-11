from django.urls import path, include
from rest_framework import routers

from task.views import TaskViewSet, StatusViewSet

router = routers.DefaultRouter()
router.register("tasks", TaskViewSet, basename="tasks")
router.register("statuses", StatusViewSet, basename="statuses")

urlpatterns = [path("", include(router.urls))]

app_name = "task"
