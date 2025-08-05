from django.conf import settings
from django.db import models


class LastThreePasswords(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_system_last_three_passwords"

    def __str__(self):
        return f"Password record for user {self.user.id}"
