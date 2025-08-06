
import os
import uuid
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from ems.models.emp_basic_profile import TblEmpBasicProfile


def get_unique_name():
    return uuid.uuid4().hex


def upload_to_profile_photo(instance, filename):
    ext = os.path.splitext(filename)[1]
    unique_name = get_unique_name()
    return (
        f"ems/emplyee/profile_photos/emp_{instance.employee_id.id}_{unique_name}{ext}"
    )


def upload_to_signature(instance, filename):
    ext = os.path.splitext(filename)[1]
    unique_name = get_unique_name()
    return f"ems/emplyee/signatures/emp_{instance.employee_id.id}_{unique_name}{ext}"


class TblEmpOfficialInformation(models.Model):
    employee_id = models.OneToOneField(
        TblEmpBasicProfile,
        on_delete=models.CASCADE,
        related_name="official_info",
        db_column="employee_id",
    )
    reporting_to = models.ForeignKey(
        TblEmpBasicProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="reporting_to",
        related_name="reporting_employees",
    )
    employment_status = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)  

    profile_photo = models.ImageField(
        upload_to=upload_to_profile_photo, null=True, blank=True
    )
    signature = models.ImageField(upload_to=upload_to_signature, null=True, blank=True)

    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "ems_emp_official_informations"

    def __str__(self):
        return f"Official Info for Employee ID {self.employee_id.id}"

    def save(self, *args, **kwargs):
        try:
            old = TblEmpOfficialInformation.objects.get(pk=self.pk)
        except TblEmpOfficialInformation.DoesNotExist:
            old = None

        super().save(*args, **kwargs)

        if old:
            if old.profile_photo and old.profile_photo != self.profile_photo:
                if os.path.isfile(old.profile_photo.path):
                    os.remove(old.profile_photo.path)

            if old.signature and old.signature != self.signature:
                if os.path.isfile(old.signature.path):
                    os.remove(old.signature.path)
