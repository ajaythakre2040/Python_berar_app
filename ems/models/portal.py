from django.db import models


class Portal(models.Model):
    portal_name = models.CharField(max_length=255,unique=True)
    portal_code = models.CharField(max_length=255,unique=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_portals"

    def __str__(self):
        return self.portal_name
