from rest_framework import serializers
from auth_system.models.login_fail_attempts import LoginFailAttempts


class LoginFailAttemptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginFailAttempts
        fields = [
            "id",
            "username",
            "ip",
            "agent_browser",
            "user_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]