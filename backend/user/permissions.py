from rest_framework.permissions import BasePermission


class IsVerifiedTeam(BasePermission):
    message = 'team is not verified'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'verification_completed', False))
