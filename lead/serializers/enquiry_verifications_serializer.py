from rest_framework import serializers
from ..models.enquiry_verifications import EnquiryVerification

class EnquiryVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryVerification
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = (
            "enquiry",
            "verified_at",
        )