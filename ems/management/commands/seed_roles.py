from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from ems.models.role import Role
from constants import EMS


class Command(BaseCommand):
    help = "Seed Roles for EMS portal"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Roles seed...")

        roles_data = [
            {
                "portal_id": EMS,
                "role_name": "Administrator",
                "role_code": "ADMIN0001",
                "created_by": 1,
            },
            {
                "portal_id": EMS,
                "role_name": "Sub-Administrator",
                "role_code": "SUBADMIN0001",
                "created_by": 1,
            },
        ]

        try:
            with transaction.atomic():
                for role_data in roles_data:
                    role, created = Role.objects.get_or_create(
                        role_code=role_data["role_code"],
                        defaults={
                            "portal_id": role_data["portal_id"],
                            "role_name": role_data["role_name"],
                            "created_by": role_data["created_by"],
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Created Role: {role.role_name}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️ Role already exists: {role.role_name}"
                            )
                        )

            self.stdout.write(self.style.SUCCESS("🎉 Roles seeded successfully!"))

        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f"❌ IntegrityError: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error occurred: {str(e)}"))
