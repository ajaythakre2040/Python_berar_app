from django.db import models


class Languages(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "code_of_conduct_languages"  # This will be the table name in the DB
        
    def __str__(self):
        return self.name

