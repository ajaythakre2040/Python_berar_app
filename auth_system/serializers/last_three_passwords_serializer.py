from rest_framework import serializers
from auth_system.models import LastThreePasswords


class LastThreePasswordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastThreePasswords
        fields = [
            "id",
            "user_id",
            "password",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]