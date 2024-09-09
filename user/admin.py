from django.contrib import admin

from user.apps import UserConfig
from user.models import User


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
