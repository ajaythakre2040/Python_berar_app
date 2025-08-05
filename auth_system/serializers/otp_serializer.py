from rest_framework import serializers
from auth_system.models.otp import OTP


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = "__all__"  
