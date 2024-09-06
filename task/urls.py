from django.urls import path, include
from rest_framework import routers

from task.views import TaskViewSet, StatusViewSet

router = routers.DefaultRouter()
router.register("tasks", TaskViewSet)
router.register("statuses", StatusViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "task"
