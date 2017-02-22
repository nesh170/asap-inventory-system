from rest_framework import permissions
from rest_framework.compat import is_authenticated


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return is_authenticated(request.user)

        # The user has to be a staff
        return is_authenticated(request.user) and request.user.is_staff


class IsSuperUserOrStaffReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return is_authenticated(request.user) and request.user.is_staff

        # The user has to be a superuser
        return is_authenticated(request.user) and request.user.is_superuser


class IsSuperUserDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method == 'DELETE':
            return is_authenticated(request.user) and request.user.is_superuser

        return is_authenticated(request.user)


class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_authenticated(request.user) and request.user.is_staff


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_authenticated(request.user) and request.user.is_superuser



