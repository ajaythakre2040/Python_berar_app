from rest_framework import serializers
from ..models.enquiry_end_user import EnquiryEnduser


class EnquiryEndUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryEnduser
        # fields = "__all__"
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )

