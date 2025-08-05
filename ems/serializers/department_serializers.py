from rest_framework import serializers
from ems.models.department import TblDepartment


class TblDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblDepartment
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "updated_by",
            "deleted_by",
            "deleted_at",
            "created_at",
            "updated_at",
        ]

    def validate_department_name(self, value):
        value = value.strip()
        if len(value) == 0:
            raise serializers.ValidationError("Department name cannot be empty.")

        qs = TblDepartment.objects.filter(
            department_name__iexact=value, deleted_at__isnull=True
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "A department with this name already exists."
            )
        return value

    def validate_department_email(self, value):
        if value:
            qs = TblDepartment.objects.filter(
                department_email__iexact=value, deleted_at__isnull=True
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError(
                    "This email is already used by another department."
                )
        return value
