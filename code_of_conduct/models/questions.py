from django.db import models
from code_of_conduct.models.languages import Languages  # Language model
from django.utils import timezone

class Questions(models.Model):
    TYPE_CHOICES = [
        ('general', 'General'),
        ('technical', 'Technical'),
        ('other', 'Other'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    is_status = models.BooleanField(default=False)
    questions = models.TextField()

    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.IntegerField(null=True, blank=True, default=None)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} - {self.questions[:30]}"
