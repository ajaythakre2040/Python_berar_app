from rest_framework import serializers
from ..models.enquiry_selfie import EnquirySelfie


class EnquirySelfieSerializer(serializers.ModelSerializer):
    selfie = serializers.ImageField(allow_empty_file=False, use_url=True)

    class Meta:
        model = EnquirySelfie
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("enquiry",)
