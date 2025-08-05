

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run all seeders (portal, menu, roles, role permissions, admin user, employee profile)"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.MIGRATE_HEADING("🚀 Starting full seed process...\n")
        )

        try:
            call_command("seed_portals")
            self.stdout.write(self.style.SUCCESS("✅ Portals seeded."))

            call_command("seed_menus")
            self.stdout.write(self.style.SUCCESS("✅ Menus seeded."))

            call_command("seed_roles")
            self.stdout.write(self.style.SUCCESS("✅ Roles seeded."))

            call_command("seed_role_permissions")
            self.stdout.write(self.style.SUCCESS("✅ Role Permissions seeded."))

            call_command("seed_employee_profile")
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Admin Employee profile & related details seeded."
                )
            )

            call_command("seed_admin_user")
            self.stdout.write(self.style.SUCCESS("✅ Admin user seeded."))

            self.stdout.write(self.style.SUCCESS("\n🎉 All seeders ran successfully!"))

        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"❌ Error occurred: {e}"))
