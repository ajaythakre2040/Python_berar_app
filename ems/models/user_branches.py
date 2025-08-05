from django.db import models


class UserBranches(models.Model):
    employee_id = models.IntegerField(null=True, blank=True)
    branch_id = models.IntegerField(null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = "ems_user_branches"

    def __str__(self):
        return f"User {self.employee_id} - Branch {self.branch_id}"
