from rest_framework import serializers
from ems.models.role_permission import RolePermission


class RolePermissionSerializer(serializers.ModelSerializer):
    portal_name = serializers.CharField(source="portal.portal_name", read_only=True)

    class Meta:

        model = RolePermission
        fields = [
            "id",
            "menu_id",
            "view",
            "add",
            "edit",
            "delete",
            "print",
            "export",
            "sms_send",
            "api_limit",
            "portal_name",  # use portal name instead of portal_id
        ]
        # exclude = [
        #     "role",  # hidden: handled via nested serializer
        #     "created_by",
        #     "updated_by",
        #     "deleted_by",
        #     "created_at",
        #     "updated_at",
        #     "deleted_at",
        # ]
        # extra_kwargs = {
        #     "portal_id": {"read_only": True},  # auto-filled in parent
        # }
