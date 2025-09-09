from django.db import models


class EnquiryEnduser(models.Model):
    title = models.CharField(max_length=255, unique=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title   
    class Meta:
        db_table = "lead_enquiry_end_user" 
