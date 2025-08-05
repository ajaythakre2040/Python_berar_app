from datetime import datetime
from django.db import models
from lead.models.enquiry import Enquiry
from django.utils import timezone
import uuid

def image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_name = uuid.uuid4().hex 
    return f'lead/images/enquiry_{instance.enquiry.id}/{unique_name}.{ext}'

class EnquiryImages(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="enquiry_images")

    premises_type = models.CharField(max_length=100)
    employee_id = models.IntegerField()

    capture_date = models.DateField(editable=False)
    capture_time = models.TimeField(editable=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    image1 = models.ImageField(upload_to=image_upload_path, null=True, blank=True)  
    image2 = models.ImageField(upload_to=image_upload_path, null=True, blank=True)
    image3 = models.ImageField(upload_to=image_upload_path, null=True, blank=True)
    image4 = models.ImageField(upload_to=image_upload_path, null=True, blank=True)
    image5 = models.ImageField(upload_to=image_upload_path, null=True, blank=True)
    image6 = models.ImageField(upload_to=image_upload_path, null=True, blank=True)

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
        return f"Image for Enquiry #{self.enquiry.id} by Employee {self.employee_id}"
    class Meta:
        db_table = "lead_enquiry_image"  # ✅ Custom table name