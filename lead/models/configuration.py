from django.db import models
from django.utils import timezone

class Configuration(models.Model):
        domain_url = models.CharField(max_length=255)
        privacy_policy = models.CharField(max_length=255)
        terms_and_condition_url = models.CharField(max_length=255)
        about_url = models.CharField(max_length=255)
        contact_us = models.CharField(max_length=255)

        created_by = models.IntegerField()
        created_at = models.DateTimeField(default=timezone.now)
        updated_by = models.IntegerField(null=True, blank=True, default=0)
        updated_at = models.DateTimeField(null=True, blank=True, default=None)
        deleted_by = models.IntegerField(null=True, blank=True, default=0)
        deleted_at = models.DateTimeField(null=True, blank=True)

        def __str__(self):
            return self.domain_url
        class Meta:
            db_table = "lead_configurations"  # ✅ Custom table namef