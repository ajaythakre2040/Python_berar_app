from rest_framework import serializers
from ..models.enquiry_images import EnquiryImages

class EnquiryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryImages
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("enquiry",)

    def validate(self, data):
        media_file = data.get("media_file")

        if not media_file:
            raise serializers.ValidationError(
                {"media_file": "At least one image is required."}
            )
        return data
