from django.db import models
from ems.models import TblDepartment

class TblDesignation(models.Model):
    department = models.ForeignKey(
        TblDepartment,
        on_delete=models.PROTECT,
        db_column='department_id',
        related_name='designations'
    )   
    parent_designation_id = models.IntegerField(null=True, blank=True, default=0)
    designation_name = models.CharField(max_length=255)
    designation_code = models.CharField(max_length=255, null=True,unique=True, blank=True)
    designation_priority = models.IntegerField(default=1)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_designations"

    def __str__(self):
        return self.designation_name
