import json
from django.utils import timezone
from django.db import DatabaseError

from auth_system.models.login_session import LoginSession
from auth_system.models.user import TblUser
from rest_framework_simplejwt.settings import api_settings

refresh_token_lifetime = api_settings.REFRESH_TOKEN_LIFETIME


def create_login_session(
    user_id, login_portal, token, ip_address=None, agent_browser=None, headers=None
):
    from auth_system.models import TblUser
    from auth_system.models.login_session import LoginSession
    from django.utils import timezone
    import traceback

    try:
        user = TblUser.objects.get(id=user_id)

        
        if len(token) > 1024:

            token = token[:1024]

        session = LoginSession.objects.create(
            user=user,
            login_portal=login_portal,
            token=token,
            ip_address=ip_address,
            agent_browser=agent_browser,
            request_headers=dict(headers) if headers else None,
            login_at=timezone.now(),
            created_at=timezone.now(),
            is_active=True,
            expiry_at=timezone.now() + refresh_token_lifetime,
        )

        return session

    except Exception as e:
        print("❌ EXCEPTION in create_login_session():", repr(e))
        traceback.print_exc()
        return None


def get_active_session(user_id, login_portal=None):
   
    filters = {
        "user_id": user_id,
        "logout_at__isnull": True,
    }
    if login_portal is not None:
        filters["login_portal"] = login_portal

    return LoginSession.objects.filter(**filters).first()


def end_session(session):
    
    try:
        session.logout_at = timezone.now()
        session.is_active = False
        session.save()
    except DatabaseError as e:
        print(f"❌ Error ending session: {e}")
