from django.core.management.base import BaseCommand
from ems.models import Portal
from django.utils import timezone  


class Command(BaseCommand):
    help = "Seed default portals"

    def handle(self, *args, **kwargs):
        portals = [
            {
                "portal_name": "Employee Management System",
                "portal_code": "EMS",
                "created_by": 1,
            },
            {
                "portal_name": "Customer Management System",
                "portal_code": "CMS",
                "created_by": 1,
            },
        ]

        for data in portals:
            portal, created = Portal.objects.get_or_create(
                portal_code=data["portal_code"],
                defaults={
                    "portal_name": data["portal_name"],
                    "created_by": data["created_by"],
                    "updated_at": timezone.now(),  
                },
            )
            msg = f"{'✅ Created' if created else '⚠️ Already exists'} portal: {data['portal_name']}"
            self.stdout.write(
                self.style.SUCCESS(msg) if created else self.style.WARNING(msg)
            )

        self.stdout.write(self.style.SUCCESS("🎉 Portals seeded successfully!"))
