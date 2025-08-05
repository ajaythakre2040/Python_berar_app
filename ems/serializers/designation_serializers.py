from rest_framework import serializers
from ems.models import TblDesignation, TblDepartment


class TblDesignationSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=TblDepartment.objects.filter(deleted_at__isnull=True),
        write_only=True,
        error_messages={
            "does_not_exist": "Invalid department ID.",
            "required": "Department ID is required.",
        },
    )
    department_name = serializers.CharField(
        source="department.department_name", read_only=True
    )

    parent_designation_name = serializers.SerializerMethodField()

    class Meta:
        model = TblDesignation
        fields = [
            "id",
            "department_id",
            "department_name",
            "parent_designation_id",  
            "parent_designation_name",  
            "designation_name",
            "designation_code",
            "designation_priority",
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
            "department_name",
            "parent_designation_name",
        )

    def get_parent_designation_name(self, obj):
        if obj.parent_designation_id:
            parent = TblDesignation.objects.filter(
                id=obj.parent_designation_id, deleted_at__isnull=True
            ).first()
            return parent.designation_name if parent else None
        return None

    

    def validate_designation_priority(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Designation priority cannot be negative."
            )
        return value

    def validate_parent_designation_id(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Parent designation ID cannot be negative."
            )
        return value
