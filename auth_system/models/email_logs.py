from django.db import models
from constants import  EmailType, DeliveryStatus


class EmailLogs(models.Model):
    user_id = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=200)
    message = models.TextField()
    email_type = models.IntegerField(choices=EmailType.choices)  
    request_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(choices=DeliveryStatus.choices)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "auth_system_email_log"

    def __str__(self):
        return f"Email to {self.email}]"
