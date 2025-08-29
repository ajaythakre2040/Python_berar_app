from rest_framework import serializers
from ..models.enquiry_images import EnquiryImages

class EnquiryImageSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

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

    def get_file_url(self, obj):
        if obj.media_file:
            return obj.media_file.url   # this gives /media/... directly
        return None
