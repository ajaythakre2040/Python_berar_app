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
        read_only_fields = (
            "enquiry",
        )

    def vaidate(self, data):
        images = [
            data.get('image1'),
            data.get('image2'),
            data.get('image3'),
            data.get('image4'),
            data.get('image5'),
            data.get('image6'),
        ]

        if not any(images):
            raise serializers.ValidationError("At Lest one image is required")
        return data