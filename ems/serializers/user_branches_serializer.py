from rest_framework import serializers
from ems.models.user_branches import UserBranches


class UserBranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBranches
        fields = [
            "id",
            "employee_id",
            "branch_id",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_at",
            "deleted_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]