from django.contrib import admin

from task.models import Task, Status, FileImage

# Register your models here.

admin.site.register(Task)
admin.site.register(Status)
admin.site.register(FileImage)