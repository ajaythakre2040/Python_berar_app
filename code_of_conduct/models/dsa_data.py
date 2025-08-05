from django.db import models
from django.utils import timezone


class DsaData(models.Model):

    quarter_code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=255, db_index=True)

    owner_name = models.CharField(max_length=255, db_index=True)

    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    adhar_number = models.CharField(max_length=20, db_index=True)
    pan_number = models.CharField(max_length=20, db_index=True)
    mobile_number = models.CharField(max_length=15, db_index=True)
    city = models.CharField(max_length=100)
    address = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.IntegerField()

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # class Meta:
    #     db_table = "dsa_data" #This will be the table name in the DB

    def __str__(self):
        return f"{self.name} | Owner: {self.owner_name} | City: {self.city} | Quarter: {self.quarter_code}"


