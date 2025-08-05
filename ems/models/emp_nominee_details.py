from django.db import models
from ems.models.emp_basic_profile import TblEmpBasicProfile


class TblEmpNomineeDetails(models.Model):

    employee_id = models.OneToOneField(
        TblEmpBasicProfile,
        on_delete=models.CASCADE,
        related_name="nominees",
        db_column="employee_id",
    )
    nominee_name = models.CharField(max_length=255, null=True, blank=True)
    nominee_relation = models.CharField(max_length=100, null=True, blank=True)
    nominee_mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    nominee_email = models.EmailField(null=True, blank=True, unique=True)
    nominee_address = models.CharField(max_length=500, null=True, blank=True)

    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "ems_emp_nominee_details"

    def __str__(self):
        return f"{self.nominee_name} ({self.nominee_relation})"
