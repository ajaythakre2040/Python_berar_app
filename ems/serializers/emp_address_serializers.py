from rest_framework import serializers
from ems.models import TblEmpAddressDetails
from ems.models.emp_basic_profile import TblEmpBasicProfile


class EmpAddressDetailsSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=TblEmpBasicProfile.objects.filter(deleted_at__isnull=True),
        required=True,
        error_messages={
            "required": "Employee ID is required.",
            "does_not_exist": "Employee does not exist or has been deleted.",
            "incorrect_type": "Invalid type. Employee ID must be an integer.",
        },
    )

    class Meta:
        model = TblEmpAddressDetails
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_at",
            "deleted_by",
        )

    def validate_pincode(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Pincode must contain only digits.")
        return value

    def validate_employee_id(self, value):
        if not TblEmpBasicProfile.objects.filter(
            id=value.id, deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError(
                "Employee does not exist or has been deleted."
            )
        return value
