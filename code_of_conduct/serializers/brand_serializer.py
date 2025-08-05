from rest_framework import serializers

from ..models.brand import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
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