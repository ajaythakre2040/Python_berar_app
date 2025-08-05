import uuid
from django.db import models
from django.utils import timezone
from constants import LOGIN_PORTAL_CHOICES
from auth_system.models import TblUser


class LoginSession(models.Model):
    user = models.ForeignKey(TblUser, on_delete=models.CASCADE)
    login_portal = models.IntegerField(
        choices=LOGIN_PORTAL_CHOICES,
        default=1,
    )
    token = models.CharField(max_length=1024, unique=True)  
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    login_at = models.DateTimeField(default=timezone.now)
    logout_at = models.DateTimeField(null=True, blank=True)
    expiry_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    agent_browser = models.CharField(max_length=255, null=True, blank=True)
    request_headers = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "auth_system_login_session"
        indexes = [
            models.Index(fields=["user", "logout_at"]),
        ]
        ordering = ["-login_at"]

    def __str__(self):
        status = "Active" if self.is_active else "Logged out"
        return f"[{status}] User ID: {self.user.id} - IP: {self.ip_address}"
