from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user


class UserViewPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == "create":
            return True
        return permissions.IsAuthenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "partial_update", "destroy"]:
            if obj.pk == request.user.pk:
                return True
            return False

        return True
