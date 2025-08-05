from django.db import models
from ems.models.emp_basic_profile import TblEmpBasicProfile
from django.utils import timezone


class TblEmpAddressDetails(models.Model):
    
    employee_id = models.OneToOneField(
        TblEmpBasicProfile,
        on_delete=models.CASCADE,
        related_name="address",
        db_column="employee_id",
    )
    state = models.CharField(max_length=200)
    district = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    address = models.CharField(max_length=355)
    pincode = models.CharField(max_length=20)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "ems_emp_address_details"

    def __str__(self):
        return f"{self.city}, {self.state} - {self.pincode}"
