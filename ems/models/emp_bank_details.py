from django.db import models
from ems.models.emp_basic_profile import TblEmpBasicProfile
from django.utils import timezone


class TblEmpBankDetails(models.Model):

    employee_id = models.OneToOneField(
        TblEmpBasicProfile,
        on_delete=models.CASCADE,
        related_name="bank_details",
        db_column="employee_id",
    )
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    branch_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)

    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "ems_emp_bank_details"

    def __str__(self):
        return f"{self.bank_name or 'Bank'} - {self.account_number or 'Account'}"
