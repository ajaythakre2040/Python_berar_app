from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from auth_system.models.user import TblUser
from constants import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    ADMIN_MOBILE,
    ADMIN_ROLE_ID,
    ADMIN_EMPLOYEE_ID,
    ADMIN_EMPLOYEE_CODE,
    ADMIN_BRANCH_ID,
    ADMIN_DEPARTMENT_ID,
    ADMIN_DESIGNATION_ID,
    ADMIN_LEVEL,
    ADMIN_FULL_NAME,
)


class Command(BaseCommand):
    help = "Seed the admin user"

    def handle(self, *args, **kwargs):
        if TblUser.objects.filter(email=ADMIN_EMAIL).exists():
            self.stdout.write(self.style.WARNING("⚠️ Admin user already exists."))
            self.stdout.write(self.style.WARNING(f"   📧 Email   : {ADMIN_EMAIL}"))
            self.stdout.write(
                self.style.WARNING(f"   🔐 Password: {ADMIN_PASSWORD} (raw)")
            )
            self.stdout.write(self.style.WARNING(f"   📱 Mobile  : {ADMIN_MOBILE}"))
            return

        user = TblUser.objects.create(
            email=ADMIN_EMAIL,
            mobile_number=ADMIN_MOBILE,
            password=make_password(ADMIN_PASSWORD),
            # role_id=ADMIN_ROLE_ID,
            employee_id=ADMIN_EMPLOYEE_ID,
            employee_code=ADMIN_EMPLOYEE_CODE,
            # branch_id=ADMIN_BRANCH_ID,
            # department_id=ADMIN_DEPARTMENT_ID,
            # designation_id=ADMIN_DESIGNATION_ID,
            level=ADMIN_LEVEL,
            full_name=ADMIN_FULL_NAME,
            created_by=ADMIN_EMPLOYEE_ID,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Admin user created:\n"
                f"   📧 Email   : {ADMIN_EMAIL}\n"
                f"   🔐 Password: {ADMIN_PASSWORD} (raw, before hashing)\n"
                f"   📱 Mobile  : {ADMIN_MOBILE}"
            )
        )
