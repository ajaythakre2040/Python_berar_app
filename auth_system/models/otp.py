from django.db import models
from django.utils import timezone
from constants import OtpType,  DeliveryStatus


class OTP(models.Model):
    user_id = models.CharField(max_length=255)
    otp_code = models.CharField(max_length=6)
    otp_type = models.IntegerField(choices=OtpType.choices)
    request_id = models.CharField(max_length=200)
    status = models.IntegerField(choices=DeliveryStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_at = models.DateTimeField()
    class Meta:
        db_table = "auth_system_otps"

    def __str__(self):
        return (
            f"OTP {self.otp_code} for Loan {self.loan_id} ({self.get_status_display()})"
        )

    def is_expired(self):
        return timezone.now() > self.expiry_at
