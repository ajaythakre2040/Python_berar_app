from django.db import models
from django.utils import timezone


class DepositAgents(models.Model):

    deposit_agents_file_upload = models.CharField(max_length=255)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.IntegerField()

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)
    file_status = models.IntegerField(default=0)

    class Meta:
        db_table = "code_of_conduct_deposit_agents_upload"
        
    def __str__(self):
        return self.deposit_agents_file


