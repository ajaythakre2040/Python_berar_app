from django.db import models
from lead.models.enquiry import Enquiry
from ems.models.emp_basic_profile import TblEmpBasicProfile
from ems.models.branch import TblBranch

class LeadAssignLog(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(TblEmpBasicProfile, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(TblBranch, on_delete=models.SET_NULL, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)

    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lead_assign_logs"
