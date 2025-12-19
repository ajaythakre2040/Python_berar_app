from rest_framework import serializers
from django.utils import timezone
from ems.models.role import Role
from ems.models.role_permission import RolePermission
from ems.serializers.role_permission_serializer import RolePermissionSerializer
from django.db import transaction
from ems.models.portal import Portal


class RoleSerializer(serializers.ModelSerializer):
    permission = RolePermissionSerializer(many=True, write_only=True)
    permissions = RolePermissionSerializer(many=True, read_only=True)
    portal_name = serializers.CharField(source="portal.portal_name", read_only=True)
    portal_id = serializers.PrimaryKeyRelatedField(
        queryset=Portal.objects.filter(deleted_at__isnull=True),
        source="portal",
        write_only=True,
        error_messages={
            "does_not_exist": "Invalid portal ID.",
            "incorrect_type": "Portal ID must be an integer.",
        },
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "portal_id",
            "portal_name",
            "role_name",
            "role_code",
            "permission",
            "permissions",
        ]
        read_only_fields = ("portal_name",)

    def validate_permission(self, value):
        seen = set()
        for item in value:
            key = item.get("menu_id")
            if key in seen:
                raise serializers.ValidationError(
                    f"Duplicate permission for menu_id={key}"
                )
            seen.add(key)
        return value

    def create(self, validated_data):
        permissions_data = validated_data.pop("permission", [])
        request = self.context.get("request")
        user_id = request.user.id if request and request.user.is_authenticated else None

        role = Role.objects.create(created_by=user_id, **validated_data)

        for perm in permissions_data:
            RolePermission.objects.create(
                role=role,
                portal_id=role.portal_id,
                created_by=user_id,
                **{k: v for k, v in perm.items() if k != "portal_id"},
            )

        return role

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop("permission", None)
        request = self.context.get("request")
        user_id = request.user.id if request and request.user.is_authenticated else None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = user_id
        instance.updated_at = timezone.now()
        instance.save()
        if permissions_data:
            with transaction.atomic():
                menu_ids = [
                    perm.get("menu_id")
                    for perm in permissions_data
                    if perm.get("menu_id")
                ]
                RolePermission.objects.filter(
                    role=instance,
                    portal_id=instance.portal_id,
                    menu_id__in=menu_ids,
                    deleted_at__isnull=True,
                ).delete()
                for perm in permissions_data:
                    menu_id = perm.get("menu_id")
                    if not menu_id:
                        continue
                    RolePermission.objects.create(
                        role=instance,
                        portal_id=instance.portal_id,
                        created_by=user_id,
                        updated_by= user_id,
                        updated_at= timezone.now(),
                        **{
                            k: v
                            for k, v in perm.items()
                            if k not in ["portal_id", "deleted_by", "deleted_at"]
                        },
                    )
        return instance

    
    
    
    
    

    
    

    
    
    

    
    
    

    
    
    
    
    
    

    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    

    
    
    

    
