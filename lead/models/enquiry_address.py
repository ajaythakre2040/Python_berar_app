
from django.db import models
from lead.models.enquiry import Enquiry
from django.utils import timezone

class EnquiryAddress(models.Model):

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="enquiry_addresses")
    premises_type = models.CharField(max_length=100)
    premises_status = models.CharField(max_length=100)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    latitude = models.CharField(max_length=200, null=True, blank=True)
    longitude = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    area = models.CharField(max_length=255)

    use_different_address = models.BooleanField(default=False)

    different_premises_type = models.CharField(max_length=100, null=True, blank=True)
    different_premises_status = models.CharField(max_length=100, null=True, blank=True)
    different_address = models.TextField(null=True, blank=True)
    different_pincode = models.CharField(max_length=10, null=True, blank=True)
    different_latitude = models.CharField(max_length=200, null=True, blank=True)
    different_longitude = models.CharField(max_length=200, null=True, blank=True)
    different_state = models.CharField(max_length=100, null=True, blank=True)
    different_district = models.CharField(max_length=100, null=True, blank=True)
    different_area = models.CharField(max_length=255, null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Enquiry #{self.enquiry.id} - Address ID #{self.id}"
    class Meta:
        db_table = "lead_enquiry_address"  # ✅ Custom table namef