

from django.core.management.base import BaseCommand
from django.db import transaction
from ems.models import Role, RolePermission
from constants import (
    EMS,
    USER,
    PORTAL,
    MENU,
    DEPARTMENT,
    DESIGNATION,
    BRANCH,
    ROLE,
    ROLEPERMISSION,
    EMPLOYEE,
    ADMIN_EMPLOYEE_ID,
)


class Command(BaseCommand):
    help = "Seed RolePermission data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding RolePermissions...")

        try:
            
            admin_role = Role.objects.get(role_code="ADMIN0001")
            subadmin_role = Role.objects.get(role_code="SUBADMIN0001")

            
            permissions_to_create = [
                
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": USER,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": PORTAL,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": MENU,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": DEPARTMENT,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": DESIGNATION,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": BRANCH,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": ROLE,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": ROLEPERMISSION,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                {
                    "portal_id": EMS,
                    "role": admin_role,
                    "menu_id": EMPLOYEE,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
                
                {
                    "portal_id": EMS,
                    "role": subadmin_role,
                    "menu_id": EMPLOYEE,
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "0",
                    "created_by": ADMIN_EMPLOYEE_ID,
                },
            ]

            
            for perm_data in permissions_to_create:
                RolePermission.objects.update_or_create(
                    role=perm_data["role"],
                    portal_id=perm_data["portal_id"],
                    menu_id=perm_data["menu_id"],
                    defaults={
                        "view": perm_data["view"],
                        "add": perm_data["add"],
                        "edit": perm_data["edit"],
                        "delete": perm_data["delete"],
                        "print": perm_data["print"],
                        "export": perm_data["export"],
                        "sms_send": perm_data["sms_send"],
                        "api_limit": perm_data["api_limit"],
                        "created_by": perm_data["created_by"],
                    },
                )

            self.stdout.write(
                self.style.SUCCESS("RolePermissions seeded successfully.")
            )

        except Role.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Role not found: {e}"))
