from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAbleToEdit(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (
                request.method not in SAFE_METHODS
                and request.user in obj.assigned_to.all()
            )
            or (request.user and request.user.is_staff)
        )
