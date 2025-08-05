
from django.core.management.base import BaseCommand
from ems.models.emp_basic_profile import TblEmpBasicProfile
from ems.models.emp_address_details import TblEmpAddressDetails
from ems.models.emp_bank_details import TblEmpBankDetails
from ems.models.emp_nominee_details import TblEmpNomineeDetails
from ems.models.emp_official_information import TblEmpOfficialInformation
from constants import (
    ADMIN_EMAIL,
    ADMIN_MOBILE,
    ADMIN_EMPLOYEE_CODE,
    ADMIN_FULL_NAME,
    ADMIN_DOB,
    ADMIN_EMPLOYEE_ID,
    ADMIN_ADDRESS,
    ADMIN_BANK_DETAILS,
    ADMIN_NOMINEE_DETAILS,
    ADMIN_OFFICIAL_INFO,
)


class Command(BaseCommand):
    help = "Seed employee profile and related tables for admin"

    def handle(self, *args, **kwargs):
        profile, created = TblEmpBasicProfile.objects.get_or_create(
            id=ADMIN_EMPLOYEE_ID,
            defaults={
                "name": ADMIN_FULL_NAME,
                "employee_code": ADMIN_EMPLOYEE_CODE,
                "email": ADMIN_EMAIL,
                "mobile_number": ADMIN_MOBILE,
                "dob": ADMIN_DOB,
                "created_by": ADMIN_EMPLOYEE_ID,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("✅ Admin employee profile created"))
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Admin employee profile already exists")
            )

        TblEmpAddressDetails.objects.get_or_create(
            employee_id=profile,
            defaults=ADMIN_ADDRESS,
        )

        TblEmpBankDetails.objects.get_or_create(
            employee_id=profile,
            defaults=ADMIN_BANK_DETAILS,
        )

        TblEmpNomineeDetails.objects.get_or_create(
            employee_id=profile,
            defaults=ADMIN_NOMINEE_DETAILS,
        )

        TblEmpOfficialInformation.objects.get_or_create(
            employee_id=profile,
            defaults=ADMIN_OFFICIAL_INFO,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "🎉 All admin employee related data created successfully!"
            )
        )
