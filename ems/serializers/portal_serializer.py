from rest_framework import serializers
from ems.models import Portal


class PortalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Portal
        fields = "__all__"  
        read_only_fields = (
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
        )
