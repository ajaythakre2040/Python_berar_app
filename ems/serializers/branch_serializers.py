from rest_framework import serializers
from ems.models import TblBranch
import re


class TblBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblBranch
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "updated_by",
            "deleted_by",
            "deleted_at",
            "created_at",
            "updated_at",
        ]

    def to_internal_value(self, data):
        # CSV se aane wale empty strings ko null (None) mein convert karna
        for field in data:
            if isinstance(data[field], str) and not data[field].strip():
                data[field] = None
        return super().to_internal_value(data)

    def validate_mobile_number(self, value):
        if value and not re.match(r"^\+?[0-9]{10,15}$", str(value)):
            raise serializers.ValidationError("Mobile number must be 10 to 15 digits.")
        return value

    def validate_secondary_mobile_number(self, value):
        if value and not re.match(r"^\+?[0-9]{10,15}$", str(value)):
            raise serializers.ValidationError(
                "Secondary mobile number must be 10 to 15 digits."
            )
        return value
