import os
import tempfile
import uuid
from io import BytesIO

from PIL import Image
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from rest_framework import status
from rest_framework.test import APIClient

from task.models import Task, Status
from task.serializers import TaskSerializer

TASK_URL = reverse("task:tasks-list")

def image_upload_url(task_id):
    """Return URL for recipe image upload"""
    return reverse("task:tasks-add-image", args=[task_id])

def detail_url(task_id):
    return reverse("task:tasks-detail", args=[task_id])


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_status(**params):
    defaults = {
        "name": uuid.uuid4()
    }
    defaults.update(params)

    return Status.objects.create(**defaults)


def sample_task(**params):
    defaults = {
        "title": "test1",
        "description": uuid.uuid1(),
    }
    defaults.update(params)

    return Task.objects.create(**defaults)


class UnauthenticatedTaskAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TASK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTaskAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = sample_user(username="test1", email="test1@gmail.com", password="qwerty12345")
        self.user2 = sample_user(username="test2", email="test2@gmail.com", password="qwerty12345")
        self.status1 = sample_status(name="Open")
        self.status2 = sample_status(name="In Progres")
        self.task1 = sample_task(status=self.status1)
        self.task2 = sample_task(title="test2", status=self.status2)
        self.task1.assigned_to.set([self.user1])
        self.task2.assigned_to.set([self.user2])

        self.client.force_authenticate(user=self.user1)

    def test_task_list(self):
        task_with_status = self.task1

        res = self.client.get(TASK_URL)
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_task_filter_by_title(self):
        res = self.client.get(TASK_URL, {"title": "test1"})

        serializer_task_1 = TaskSerializer(self.task1)
        serializer_task_2 = TaskSerializer(self.task2)

        self.assertIn(serializer_task_1.data, res.data)
        self.assertNotIn(serializer_task_2.data, res.data)

    def test_task_filter_by_genre(self):
        res = self.client.get(TASK_URL, {"status": f"{self.status1.id}"})

        serializer_task_1 = TaskSerializer(self.task1)
        serializer_task_2 = TaskSerializer(self.task2)

        self.assertIn(serializer_task_1.data, res.data)
        self.assertNotIn(serializer_task_2.data, res.data)

    def test_task_filter_by_assigned_to(self):
        assigned_to = self.task1.assigned_to.first()
        res = self.client.get(TASK_URL, {"assigned_to": f"{assigned_to.id}"})

        serializer_task_1 = TaskSerializer(self.task1)
        serializer_task_2 = TaskSerializer(self.task2)

        self.assertIn(serializer_task_1.data, res.data)
        self.assertNotIn(serializer_task_2.data, res.data)

    def test_retrieve_bus_detail(self):
        res = self.client.get(detail_url(self.task1.id))
        serializer = TaskSerializer(self.task1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_task_delete(self):
        res = self.client.delete(detail_url(self.task1.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_task(self):
        payload = {
            "title": "Test Task",
            "description": "This is a test task.",
            "status": self.status1.id,
            "assigned_to": self.user1.id,
        }

        res = self.client.post(TASK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Task")
        self.assertEqual(mail.outbox[0].body, "This is a test task.")
        self.assertEqual(mail.outbox[0].to, [self.user1.email])


class TaskImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(username="test1", email="test1@gmail.com", password="qwerty12345")
        self.status = sample_status(name="Open")
        self.task = sample_task(status=self.status)
        self.task.assigned_to.set([self.user])

        self.client.force_authenticate(user=self.user)

    def test_upload_image_to_movie(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.task.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.task.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.task.image.path))

    def test_upload_task_bad_request(self):
        url = image_upload_url(self.task.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

