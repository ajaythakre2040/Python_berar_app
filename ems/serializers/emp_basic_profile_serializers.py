from rest_framework import serializers
from ems.models import TblEmpBasicProfile
from ems.models.emp_address_details import TblEmpAddressDetails
from ems.models.emp_bank_details import TblEmpBankDetails
from ems.models.emp_nominee_details import TblEmpNomineeDetails
from ems.models.emp_official_information import TblEmpOfficialInformation

from .emp_address_serializers import EmpAddressDetailsSerializer
from .emp_bank_serializers import TblEmpBankDetailsSerializer
from .emp_nominee_serializers import TblEmpNomineeDetailsSerializer
from .emp_official_info_serializers import TblEmpOfficialInformationSerializer


class EmpBasicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblEmpBasicProfile
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        )

    def validate_mobile_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Mobile number must be exactly 10 digits."
            )
        return value

    def validate_gender(self, value):
        valid_genders = ["Male", "Female", "Other"]
        if value not in valid_genders:
            raise serializers.ValidationError(f"Gender must be one of {valid_genders}.")
        return value


class FullEmployeeProfileSerializer(serializers.ModelSerializer):
    # Nested related data included via SerializerMethodField

    address_details = serializers.SerializerMethodField()
    bank_details = serializers.SerializerMethodField()
    nominee_details = serializers.SerializerMethodField()
    official_info = serializers.SerializerMethodField()

    class Meta:
        model = TblEmpBasicProfile
        fields = (
            "id",
            "name",
            "employee_code",
            "email",
            "mobile_number",
            "dob",
            "gender",
            "address_details",
            "bank_details",
            "nominee_details",
            "official_info",
        )

    def get_address_details(self, obj):
        addresses = TblEmpAddressDetails.objects.filter(employee_id=obj, deleted_at__isnull=True)
        return EmpAddressDetailsSerializer(addresses, many=True).data

    def get_bank_details(self, obj):
        banks = TblEmpBankDetails.objects.filter(employee_id=obj, deleted_at__isnull=True)
        return TblEmpBankDetailsSerializer(banks, many=True).data

    def get_nominee_details(self, obj):
        nominees = TblEmpNomineeDetails.objects.filter(employee_id=obj, deleted_at__isnull=True)
        return TblEmpNomineeDetailsSerializer(nominees, many=True).data

    def get_official_info(self, obj):
        try:
            official = TblEmpOfficialInformation.objects.get(employee_id=obj, deleted_at__isnull=True)
            return TblEmpOfficialInformationSerializer(official).data
        except TblEmpOfficialInformation.DoesNotExist:
            return None