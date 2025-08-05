from django.db import models
from auth_system.models import TblUser  # ✅ Import your actual custom user model


class BlackListedToken(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(
        TblUser, on_delete=models.CASCADE
    )  # ✅ Linked to the correct custom user model

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("token", "user")

    def __str__(self):
        return f"Token {self.token} blacklisted for {self.user}"
