from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.timezone import now
from datetime import timedelta
from constants import PORTAL_URL_MAP

SKIP_PORTAL_CHECK_PREFIXES = ["auth_system", "api-docs", "swagger", "redoc"]
LAST_ACTIVITY_UPDATE_THRESHOLD = timedelta(
    seconds=30
)  


class PortalJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)
        if user_auth_tuple is None:
            return None

        user, validated_token = user_auth_tuple

        
        now_time = now()
        if (
            not user.last_activity
            or (now_time - user.last_activity) > LAST_ACTIVITY_UPDATE_THRESHOLD
        ):
            user.last_activity = now_time
            user.save(update_fields=["last_activity"])

        
        path_parts = request.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise AuthenticationFailed("Invalid API path. Access denied.")

        portal_name = path_parts[1].lower()
        if portal_name in SKIP_PORTAL_CHECK_PREFIXES:
            return user, validated_token

        required_portal_id = PORTAL_URL_MAP.get(portal_name)
        if required_portal_id is None:
            raise AuthenticationFailed("Unauthorized access. Invalid portal.")

        token_portal_id_raw = validated_token.get("portal_id")
        try:
            token_portal_id = int(token_portal_id_raw)
        except (TypeError, ValueError):
            raise AuthenticationFailed("Invalid portal_id in token")

        if token_portal_id != required_portal_id:
            raise AuthenticationFailed(
                "Permission denied. Token does not match portal access."
            )

        return user, validated_token
