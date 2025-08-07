from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from auth_system.models.blacklist import BlackListedToken
from auth_system.models.login_session import LoginSession
from auth_system.utils.common import get_client_ip_and_agent


class IsTokenValid(BasePermission):
    """
    Permission class to ensure:
    1. Token is present and structurally valid
    2. Token is not blacklisted (i.e., the user has not logged out)
    3. Token is being used from the same IP and browser (agent)
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

        # --- IP and Agent Check ---
        ip, agent = get_client_ip_and_agent(request)
        session = LoginSession.objects.filter(
            user=user.id,
            token=raw_token,
            is_active=True,
            logout_at__isnull=True,
            ip_address=ip,
            agent_browser=agent,
        ).first()
        if not session:
            self.message = "Your session is not valid for this device or browser."
            return False

        return True
