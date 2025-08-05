from rest_framework import serializers
from auth_system.models.password_attempt import PasswordAttemptLogs


class PasswordAttemptLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordAttemptLogs
        fields = [
            "id",
            "ip",
            "agent_browser",
            "user_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]