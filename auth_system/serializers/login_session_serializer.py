from rest_framework import serializers
from auth_system.models.login_session import LoginSession


class LoginSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginSession
        fields = "__all__"
