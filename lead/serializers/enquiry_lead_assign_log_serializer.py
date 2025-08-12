from rest_framework import serializers

from ..models.enquiry_lead_assign_log import LeadAssignLog

class LeadAssignLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadAssignLog
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
