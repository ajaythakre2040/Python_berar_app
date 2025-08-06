import random
import string
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import CommonPasswordValidator

User = get_user_model()


def generate_token(user):
    if not isinstance(user, User):
        raise TypeError("Expected a user instance of AUTH_USER_MODEL.")
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))


def token_expiry_time(minutes=30):
    return timezone.now() + timedelta(minutes=minutes)


def otp_expiry_time(minutes=5):
    return timezone.now() + timedelta(minutes=minutes)



def validate_password(password):
    errors = []

    # Custom validation rules
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")

    # Check against common passwords
    try:
        common_validator = CommonPasswordValidator()
        common_validator.validate(password)
    except ValidationError as e:
        errors.extend(e.messages)

    # Raise all collected errors
    if errors:
        raise ValidationError(errors)


def generate_request_id(length=12):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_client_ip_and_agent(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = (
        x_forwarded_for.split(",")[0].strip()
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR", "127.0.0.1")
    )
    agent = request.META.get("HTTP_USER_AGENT", "Unknown")
    return ip, agent
