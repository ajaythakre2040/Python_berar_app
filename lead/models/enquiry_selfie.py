from django.db import models
from datetime import datetime
from lead.models.enquiry import Enquiry
from django.utils import timezone
import uuid

def selfies_upload_path(instance, filename):
    
    ext = filename.split('.')[-1]
    unique_name = uuid.uuid4().hex 
    return f'lead/selfies/enquiry_{instance.enquiry.id}/{unique_name}.{ext}'

class EnquirySelfie(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="enquiry_selfies")

    premises_type = models.CharField(max_length=100)
    # employee_id = models.IntegerField()
    employee_code = models.CharField()

    capture_date = models.DateField(editable=False)
    capture_time = models.TimeField(editable=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    selfie = models.ImageField(upload_to=selfies_upload_path, null=True, blank=True)  

    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=None)

    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            now = datetime.now()
            self.capture_date = now.date()
            self.capture_time = now.time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Selfie for Enquiry #{self.enquiry.id} by Employee {self.employee_id}"
    class Meta:
        db_table = "lead_enquiry_selfie"