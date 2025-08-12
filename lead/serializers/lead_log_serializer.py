from rest_framework import serializers
from ..models.lead_logs import LeadLog

class LeadLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadLog
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
