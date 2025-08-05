from rest_framework import serializers
from auth_system.models import ForgotPassword


class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForgotPassword
        fields = [
            "id",
            "user_id",
            "password_reset_token",
            "password_reset_expires",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]