from rest_framework_simplejwt.tokens import RefreshToken


def generate_token(user, portal_id) -> dict:
    refresh = RefreshToken.for_user(user)

    refresh["user_id"] = user.id
    refresh["mobile_number"] = getattr(user, "mobile_number", None)
    refresh["email"] = getattr(user, "email", "")
    refresh["full_name"] = getattr(user, "full_name", "")
    refresh["role_id"] = getattr(user.role_id, "id", 0)
    refresh["portal_id"] = portal_id

    access = refresh.access_token
    access["user_id"] = user.id
    access["mobile_number"] = getattr(user, "mobile_number", None)
    access["email"] = getattr(user, "email", "")
    access["full_name"] = getattr(user, "full_name", "")
    access["role_id"] = user.role_id.id if user.role_id else 0
    access["portal_id"] = portal_id

    return {
        "access": str(access),
        "refresh": str(refresh),
    }
