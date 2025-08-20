from django.db import models

class QuarterMaster(models.Model):
    quarter = models.CharField(max_length=255, unique=True)
    
    from_date = models.DateField()
    to_date = models.DateField()    

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "code_of_conduct_quarter_master"
        
    def __str__(self):
        return f"{self.quarter} ({self.from_date} to {self.to_date})"
