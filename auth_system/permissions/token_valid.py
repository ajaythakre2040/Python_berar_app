from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from auth_system.models.blacklist import BlackListedToken


class IsTokenValid(BasePermission):
    """
    Permission class to ensure:
    1. Token is present and structurally valid
    2. Token is not blacklisted (i.e., the user has not logged out)
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):

        raw_token = (
            request.META.get("HTTP_AUTHORIZATION", "").replace("Bearer", "").strip()
        )

        user = request.user

        if not raw_token or not user or not user.is_authenticated:
            self.message = "Authentication credentials are missing or the user is not authenticated."
            return False

        if BlackListedToken.objects.filter(token=raw_token, user=user).exists():
            self.message = (
                "Your session has expired or you have logged out. Please sign in again."
            )
            return False

        try:
            UntypedToken(raw_token)
        except (InvalidToken, TokenError):
            self.message = "Your token is invalid or has expired. Please login again."
            return False

        return True
