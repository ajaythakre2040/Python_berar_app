from django.db import models
from ems.models.portal import Portal


class Role(models.Model):
    portal = models.ForeignKey(
        Portal,
        on_delete=models.PROTECT,
        db_column="portal_id",  # keep database column name the same
        related_name="roles",
    )
    role_name = models.CharField(max_length=255)
    role_code = models.CharField(max_length=255, unique=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.role_name
