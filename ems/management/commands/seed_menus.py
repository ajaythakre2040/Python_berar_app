from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from ems.models import Menu, Portal
from constants import EMS


class Command(BaseCommand):
    help = "Seeds predefined menu items for the EMS portal in a safe, idempotent way."

    MENU_DEFINITIONS = [
        {"menu_name": "Dashboard", "menu_code": "DA0001"},
        {"menu_name": "Portal", "menu_code": "PO0001"},
        {"menu_name": "Menu", "menu_code": "ME0001"},
        {"menu_name": "Department", "menu_code": "DE0001"},
        {"menu_name": "Designation", "menu_code": "DS0001"},
        {"menu_name": "Branch", "menu_code": "BR0001"},
        {"menu_name": "Role", "menu_code": "RO0001"},
        {"menu_name": "RolePermission", "menu_code": "RP0001"},
        {"menu_name": "Employee", "menu_code": "EM0001"},
    ]

    def handle(self, *args, **kwargs):
        """
        Main command handler to seed menus for EMS portal.
        """
        self.stdout.write(self.style.MIGRATE_HEADING("🔄 Seeding EMS Menu Items..."))

        try:
            portal = Portal.objects.get(id=EMS)
        except Portal.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    "❌ EMS portal not found. Please seed the portal first."
                )
            )
            return

        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            for index, menu in enumerate(self.MENU_DEFINITIONS, start=1):
                obj, created = Menu.objects.get_or_create(
                    menu_code=menu["menu_code"],
                    defaults={
                        "portal_id": portal.id,
                        "menu_id": 0,
                        "menu_name": menu["menu_name"],
                        "menu_order_no": index,
                        "created_by": 1,
                        "updated_at": timezone.now(),
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Created menu: {obj.menu_name}")
                    )
                    created_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ Skipped existing menu: {obj.menu_name}")
                    )
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Menu seeding complete."))
        self.stdout.write(self.style.SUCCESS(f"✔️ Created: {created_count}"))
        self.stdout.write(
            self.style.SUCCESS(f"➖ Skipped (already existed): {skipped_count}")
        )
