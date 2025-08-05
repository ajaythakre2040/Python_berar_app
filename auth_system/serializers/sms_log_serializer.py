from rest_framework import serializers
from auth_system.models.sms_log import SmsLog


class SmsLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsLog
        fields = "__all__"  
