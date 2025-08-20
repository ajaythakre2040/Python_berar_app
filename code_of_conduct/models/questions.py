from django.db import models
from django.utils import timezone
from code_of_conduct.models.languages import Languages
from constants import QuestionTypeConstants  # import constants

class Questions(models.Model):

    type = models.PositiveSmallIntegerField(
        choices=QuestionTypeConstants.CHOICES, null=True, blank=True
    )

    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    is_status = models.BooleanField(default=False)
    questions = models.TextField()

    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.IntegerField(null=True, blank=True, default=None)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "code_of_conduct_questions"  # This will be the table name in the DB

    def __str__(self):
        return f"{self.get_type_constant_display()} - {self.questions[:30]}"
