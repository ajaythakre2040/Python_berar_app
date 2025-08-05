from rest_framework import serializers
from ..models.enquiry_selfie import EnquirySelfie

class EnquirySelfieSerializer(serializers.ModelSerializer):
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

    def validate(self, data):
        selfies = [
            data.get("selfie1"),
            data.get("selfie2"),
            data.get("selfie3"),
            data.get("selfie4"),
            data.get("selfie5"),
            data.get("selfie6"),
        ]

        if not any(selfies):
            raise serializers.ValidationError("At least one selfie is required.")
        return data
