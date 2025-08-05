from django.db import models


class TblDepartment(models.Model):
    department_name = models.CharField(max_length=255)
    department_email = models.EmailField(null=True, blank=True)
    hide_from_client = models.BooleanField(default=False)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_departments"

    def __str__(self):
        return self.department_name
