from django.db import models
from django.utils import timezone
from lead.models.enquiry import Enquiry
from constants import MOBILE_STATUS_CHOICES ,EMAIL_STATUS_CHOICES, MOBILE_PENDING ,EMAIL_PENDING

class EnquiryVerification(models.Model):
    enquiry = models.OneToOneField(Enquiry, on_delete=models.CASCADE, related_name='enquiry_verification')

    mobile = models.CharField(max_length=15, null=True, blank=True)
    # mobile_verified = models.BooleanField(default=False)
    mobile_status = models.IntegerField(choices=MOBILE_STATUS_CHOICES, default=MOBILE_PENDING)

    email = models.EmailField(null=True, blank=True)
    # email_verified = models.BooleanField(default=False)
    email_verified = models.IntegerField(choices=EMAIL_STATUS_CHOICES, default=EMAIL_PENDING)

    aadhaar = models.CharField(max_length=20, null=True, blank=True)
    aadhaar_verified = models.BooleanField(default=False)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True)

    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Enquiry #{self.enquiry.id} Verifications - Mobile: {self.mobile_verified}, Email: {self.email_verified}, Aadhaar: {self.aadhaar_verified}"
    class Meta:
        db_table = "lead_enquiry_verifications"