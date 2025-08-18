from django.db import models
# from django.utils import timezone
from code_of_conduct.models.questions import Questions
from code_of_conduct.models.languages import Languages
from code_of_conduct.models.quarter_master import QuarterMaster
from constants import QuestionTypeConstants  # import constants


class AssignQuarter(models.Model):
    # TYPE_CHOICES = (
    #     ('DSA', 'DSA'),
    #     ('RSA', 'RSA'),
    #     ('DepositAgent', 'DepositAgent'),
    # )

    # type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    type = models.PositiveSmallIntegerField(
        choices=QuestionTypeConstants.CHOICES, null=True, blank=True
    )
    
    language = models.ForeignKey(Languages, on_delete=models.CASCADE ,null=True, blank=True)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE ,null=True, blank=True)
    quarter = models.ForeignKey(QuarterMaster, on_delete=models.CASCADE, null=True, blank=True)  # TEMPORARILY nullable

    created_by = models.IntegerField()
    created_at = models.DateTimeField()
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "code_of_conduct_assign_quarter"

    def __str__(self):
        return f"{self.type} - {self.language.name} - {self.quarter.code if self.quarter else 'N/A'}"
