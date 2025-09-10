

from rest_framework import serializers
from ..models.enquiry_tickets import EnquiryTickets

class EnquiryTicketSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    # attachment = serializers.FileField(use_url=False, read_only=True)
    attachment = serializers.FileField(required=False, use_url=True)

    class Meta:
        model = EnquiryTickets
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id",)
def get_attachment(self, obj):
    # Return only relative media path like "attachments/file.pdf"
    return obj.attachment.name if obj.attachment else None
