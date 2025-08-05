# ems/models/role_permission.py

from django.db import models
from ems.models.portal import Portal
from ems.models.role import Role  # Ensure correct import


class RolePermission(models.Model):
    portal = models.ForeignKey(
        "ems.Portal",
        on_delete=models.PROTECT,
        db_column="portal_id",
        related_name="role_permissions"
    )    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    menu_id = models.IntegerField()

    view = models.BooleanField(default=False)
    add = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    print = models.BooleanField(default=False)
    export = models.BooleanField(default=False)
    sms_send = models.BooleanField(default=False)
    api_limit = models.CharField(max_length=255, null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_role_permissions"
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        constraints = [
            models.UniqueConstraint(
                fields=["role", "portal_id", "menu_id"],
                name="unique_role_portal_menu"
            )
        ]

    def __str__(self):
        return f"Permission: Role {self.role_id} - Menu {self.menu_id}"
