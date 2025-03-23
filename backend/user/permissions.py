from rest_framework.permissions import BasePermission


class IsVerifiedTeam(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'varification_completed', False))
