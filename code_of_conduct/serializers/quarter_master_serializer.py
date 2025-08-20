from rest_framework import serializers

from ..models.quarter_master import QuarterMaster


class QuarterMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuarterMaster
        fields = '__all__'
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        ]