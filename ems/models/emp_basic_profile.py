from django.db import models
from django.utils import timezone

class TblEmpBasicProfile(models.Model):
    name = models.CharField(max_length=255)
    employee_code = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    # whatsapp_mobile_number = models.CharField(max_length=15,null=True, blank=True)

    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    class Meta:
        db_table = 'ems_emp_basic_profile'

    def __str__(self):
        return f"{self.name} - {self.employee_code}"
