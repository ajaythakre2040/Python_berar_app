from django.db import models
from django.utils import timezone
import uuid
from constants import TicketStatus, TicketPriority

def attachment_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_name = uuid.uuid4().hex 
    return f'lead/attachment/ticket_{unique_name}.{ext}'

class EnquiryTickets(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField()
    attachment = models.FileField(upload_to=attachment_path)
    priority = models.IntegerField(choices=TicketPriority.choices)
    status = models.IntegerField(choices=TicketStatus.choices, default=TicketStatus.TICKET_OPEN)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True)

    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    class Meta:
        db_table = "lead_enquiry_tickets" 