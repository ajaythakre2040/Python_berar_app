from rest_framework import serializers
from ems.models import Menu
from ems.models.portal import Portal


class MenuSerializer(serializers.ModelSerializer):

    portal_name = serializers.CharField(source="portal.portal_name", read_only=True)

    portal_id = serializers.PrimaryKeyRelatedField(
        queryset=Portal.objects.filter(deleted_at__isnull=True),
        source="portal",
        # write_only=True,
        error_messages={
            "does_not_exist": "Invalid portal ID.",
            "incorrect_type": "Portal ID must be an integer.",
        },
    )

    class Meta:
        model = Menu
        fields = [
            "id",
            "portal_id",
            "portal_name",
            "menu_id",
            "menu_name",
            "menu_code",
            "menu_order_no",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        ]
        read_only_fields = (
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
            "portal_name",
        )

    def validate_menu_order_no(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Menu order number cannot be negative.")
        return value
