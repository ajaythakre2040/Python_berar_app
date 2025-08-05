from django.db import models
from ems.models.portal import Portal

class Menu(models.Model):
    portal = models.ForeignKey(
        Portal,
        on_delete=models.PROTECT,
        db_column="portal_id",  
        related_name="menus",
    )
    menu_id = models.IntegerField(default=0, null=True, blank=True)
    menu_name = models.CharField(max_length=255 ,unique=True)
    menu_code = models.CharField(max_length=255, unique=True)
    menu_order_no = models.IntegerField(null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_menus"

    def __str__(self):
        return self.menu_name
