from django.db import models


class PasswordAttemptLogs(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True)
    agent_browser = models.TextField(null=True, blank=True)
    user_details = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "auth_system_password_attempt_logs"

    def __str__(self):
        return f"Login attempt from {self.ip} at {self.created_at}"
