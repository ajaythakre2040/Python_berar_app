from rest_framework import serializers
from ..models.enquiry_address import EnquiryAddress

class EnquiryAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnquiryAddress
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
        )