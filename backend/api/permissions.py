from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Пермишен дающий доступ админу, либо только чтение"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or request.user.is_admin
        )


class AuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Пермишен дающий доступ автору, админу либо только чтение"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
        )
