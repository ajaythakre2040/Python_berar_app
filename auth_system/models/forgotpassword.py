from django.db import models


class ForgotPassword(models.Model):
    user_id = models.IntegerField()
    password_reset_token = models.CharField(max_length=255)
    password_reset_expires = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_system_forgot_passwords"

    def __str__(self):
        return f"Password reset request for user {self.user_id}"
