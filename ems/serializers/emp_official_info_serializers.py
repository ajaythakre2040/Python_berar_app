from rest_framework import serializers
from ems.models.branch import TblBranch
from ems.models.emp_official_information import TblEmpOfficialInformation
from auth_system.models.user import TblUser
from ems.models.user_branches import UserBranches
from ems.models.emp_basic_profile import TblEmpBasicProfile


class TblUserMiniSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.branch_name", read_only=True)
    department_name = serializers.CharField(
        source="department.department_name", read_only=True
    )
    designation_name = serializers.CharField(
        source="designation.designation_name", read_only=True
    )
    role_name = serializers.CharField(source="role.role_name", read_only=True)

    class Meta:
        model = TblUser
        fields = [
            "employee_id",
            "branch_id",
            "branch_name",
            "department_id",
            "department_name",
            "designation_id",
            "designation_name",
            "level",
            "two_step",
            "role_id",
            "role_name",
        ]


class TblEmpOfficialInformationSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    multibranch_id = serializers.SerializerMethodField()
    reporting_to_name = serializers.CharField(
        source="reporting_to.name", read_only=True
    )

    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=TblEmpBasicProfile.objects.filter(deleted_at__isnull=True),
        error_messages={
            "required": "Employee ID is required.",
            "does_not_exist": "Employee does not exist or has been deleted.",
            "incorrect_type": "Invalid type. Employee ID must be an integer.",
        },
    )

    class Meta:
        model = TblEmpOfficialInformation
        fields = [
            "id",
            "employee_id",
            "reporting_to",
            "reporting_to_name",
            "employment_status",
            "remarks",
            "profile_photo",
            "signature",
            "user_info",
            "multibranch_id",
        ]

    def get_user_info(self, obj):
        try:
            user = TblUser.objects.get(
                employee_id=obj.employee_id.id, deleted_at__isnull=True
            )
            return TblUserMiniSerializer(user).data
        except TblUser.DoesNotExist:
            return None

    def get_multibranch_id(self, obj):
        user_branches = UserBranches.objects.filter(
            employee_id=obj.employee_id.id,
            deleted_at__isnull=True,
        )

        branch_ids = [ub.branch_id for ub in user_branches]

        branches = TblBranch.objects.filter(
            id__in=branch_ids,
            deleted_at__isnull=True,
        )

        # return [{"branch_id": b.id, "branch_name": b.branch_name} for b in branches]
        return [b.branch_name for b in branches]
        # result = []
        # for b in branches:
        #     result.extend([b.id, b.branch_name])
        # return result
