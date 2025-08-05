from django.db import models
from django.utils import timezone

class Ras(models.Model):

    ras_file_upload = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.IntegerField()

    update_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)
    file_status = models.IntegerField(default=0)
    output_file = models.CharField(max_length=255, null=True, blank=True, default=None)

    class Meta:
        db_table = "code_of_conduct_ras"  # This will be the table name in the DB

    def __str__(self):
        return self.ras_file_upload

