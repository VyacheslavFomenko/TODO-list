from unittest import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from task.models import Task, Status

TASK_URL = reverse("task:tasks-list")


def status_sample(**params):
    defaults = {
        "name": "In Progres"
    }
    defaults.update(params)

    return Status.objects.create(**defaults)


def task_sample(**params):
    defaults = {
        "title": "Test task",
        "description": "test",
        "status": status_sample(),
        "assigned_to": get_user_model().objects.create_usre(
            username="user_test", email="user_test@gmail.com", password="qwerty12345"
        )

    }
    defaults.update(params)

    return Task.objects.create(**defaults)


class UnauthenticatedTaskAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(reverse(TASK_URL))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTaskAPITests(TestCase):
    def setUp(self):
        ...
