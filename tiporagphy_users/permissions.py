from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


# from tiporagphy_users import redis_pi


class CheckAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous or request.user.is_authenticated:
            return True
        else:
            raise PermissionDenied()


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser:
            raise PermissionDenied
        return True
