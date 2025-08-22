from rest_framework import serializers
from auth_system.models.user import TblUser

class EmployeeSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch_id.branch_name', read_only=True)

    class Meta:
        model = TblUser
        fields = ['id', 'full_name', 'employee_code', 'branch_name']