from rest_framework import serializers

from ..models.quarter_master import QuarterMaster


class QuarterMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuarterMaster
        # fields = "__all__"
        exclude = ('created_by', 'updated_by', 'deleted_by', 'created_at', 'updated_at', 'deleted_at')

        # read_only_fields = (
        #     "created_by",
        #     "updated_by",
        #     "deleted_by",
        #     "created_at",
        #     "updated_at",
        #     "deleted_at",
        # )
# 