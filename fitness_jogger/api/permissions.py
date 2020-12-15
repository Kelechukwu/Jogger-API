from rest_framework import permissions
from .models import ADMIN, USER_MANAGER


class IsAdminRole(permissions.BasePermission):
    """
    Global permission check for Admin Role
    """

    def has_permission(self, request, view):
        return request.user.role == ADMIN


class IsUserManagerRole(permissions.BasePermission):
    """
    Global permission check for User Manager Role
    """

    def has_permission(self, request, view):
        return request.user.role == USER_MANAGER


class CanCRUDUsers(permissions.BasePermission):
    """
    Global permission check for Admin or User Manager Role
    """

    def has_permission(self, request, view):
        return request.user.role in [ADMIN, USER_MANAGER]


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):

        if request.user.role == ADMIN:
            return True
        return obj.user == request.user


class IsUserOwner(permissions.BasePermission):
    """
    Object-level permission to only allow user to access their own profile.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in [ADMIN, USER_MANAGER]:
            return True

        return obj == request.user
