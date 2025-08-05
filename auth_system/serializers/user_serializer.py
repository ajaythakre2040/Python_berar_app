from rest_framework import serializers
from auth_system.models.user import TblUser
from django.contrib.auth.hashers import make_password
import re


class TblUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = TblUser
        fields = [
            "id",
            "role_id",
            "employee_id",
            "employee_code",
            "branch_id",
            "department_id",
            "designation_id",
            "level",
            "full_name",
            "email",
            "mobile_number",
            "password",
            "confirm_password",
            "is_login",
            "two_step",
            "is_active",
            "is_deleted",
            "login_attempt",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_at",
            "deleted_by",
        ]
       
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "mobile_number": {"required": True},
            "full_name": {"required": True},
        }
   
    def validate_mobile_number(self, value):
        if not re.match(r"^\d{10}$", value):
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                {"password": "Password must be at least 8 characters long."}
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                {"password": "Password must contain at least one digit."}
            )
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError(
                {"password": "Password must contain at least one letter."}
            )
        return value

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        if data.get("is_deleted") and not data.get("deleted_at"):
            raise serializers.ValidationError(
                {
                    "deleted_at": 'If the user is marked as deleted, the "deleted_at" field must be set.'
                }
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)
