from django.db import models
from lead.models.enquiry import Enquiry
from constants import EnquiryStatus

class LeadLog(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=EnquiryStatus.choices, default=EnquiryStatus.DRAFT)
    remark = models.TextField(null=True, blank=True)
    followup_pickup_date = models.DateField(null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)

    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lead_logs"
