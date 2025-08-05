from rest_framework import serializers
from ..models.product_type import ProductType


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
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
