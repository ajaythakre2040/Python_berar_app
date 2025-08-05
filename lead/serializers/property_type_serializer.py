from rest_framework import serializers
from ..models.property_type import PropertyType


class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        # fields = "__all__"
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )

        # read_only_fields = (
        #     "created_by",
        #     "updated_by",
        #     "deleted_by",
        #     "created_at",
        #     "updated_at",
        #     "deleted_at",
        # )
