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
    def validate_email(self, value):
        if value and not serializers.EmailField().to_internal_value(value):
            raise serializers.ValidationError("Must be a valid email address.")
        return value

    def validate_secondary_email(self, value):
        if value and not serializers.EmailField().to_internal_value(value):
            raise serializers.ValidationError(
                "Must be a valid secondary email address."
            )
        return value

    def validate_mobile_number(self, value):
        if value and not re.match(r"^\+?[0-9]{10,15}$", value):
            raise serializers.ValidationError(
                "Mobile number must be 10 to 15 digits, optionally starting with +"
            )
        return value

    def validate_secondary_mobile_number(self, value):
        if value and not re.match(r"^\+?[0-9]{10,15}$", value):
            raise serializers.ValidationError(
                "Secondary mobile number must be 10 to 15 digits, optionally starting with +"
            )
        return value
