from django.db import models


class TblBranch(models.Model):
    branch_name = models.CharField(max_length=255)
    branch_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    branch_code = models.CharField(max_length=255, unique=True)
    email = models.EmailField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    gstin = models.CharField(max_length=15, null=True, blank=True)
    agreement_limit = models.CharField(max_length=255, null=True, blank=True)
    secondary_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    secondary_email = models.EmailField(null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    address_1 = models.TextField(null=True, blank=True)
    address_2 = models.TextField(null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    latitude = models.CharField(max_length=20, null=True, blank=True)
    longitude = models.CharField(max_length=20, null=True, blank=True)
    range = models.CharField(max_length=255, null=True, blank=True)
    state_group_code = models.CharField(max_length=255, null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_branches"

    def __str__(self):
        return self.branch_name
