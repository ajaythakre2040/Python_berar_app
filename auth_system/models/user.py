from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
import re

class TblUserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError("Mobile number is required.")
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(mobile_number, password, **extra_fields)


class TblUser(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    mobile_number = models.CharField(max_length=15, unique=True, db_index=True)
    employee_id = models.IntegerField(unique=True)
    employee_code = models.CharField(max_length=100, null=True, blank=True)
    # role_id = models.IntegerField(default=0)
    # branch_id = models.IntegerField(default=0)
    # department_id = models.IntegerField(default=0)
    # designation_id = models.IntegerField(default=0)
    branch = models.ForeignKey(
        "ems.TblBranch", on_delete=models.SET_NULL, null=True, db_column="branch_id"
    )

    department = models.ForeignKey(
        "ems.TblDepartment", on_delete=models.SET_NULL, null=True, db_column="department_id"
    )

    designation = models.ForeignKey(
        "ems.TblDesignation", on_delete=models.SET_NULL, null=True, db_column="designation_id"
    )

    role = models.ForeignKey(
        "ems.Role", on_delete=models.SET_NULL, null=True, db_column="role_id"
    )
    level = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_login = models.BooleanField(default=False)
    two_step = models.BooleanField(default=False)

    login_attempt = models.IntegerField(default=0, null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = TblUserManager()

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = ["email", "full_name"]

    class Meta:
        db_table = "auth_system_user"

    def clean(self):
        if not re.match(r"^\+?[0-9]{10,15}$", self.mobile_number):
            raise ValidationError(
                "Mobile number must be valid (10–15 digits, optional +)."
            )

    def __str__(self):
        return self.full_name
