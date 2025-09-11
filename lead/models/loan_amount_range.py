from django.db import models


class LoanAmountRange(models.Model):
    loan_amount_from = models.IntegerField(null=True, blank=True)
    loan_amount_to = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.loan_amount_from} - {self.loan_amount_to}"

    class Meta:
        db_table = "lead_loan_amount_range" 
        verbose_name = "Loan Amount Range"
        verbose_name_plural = "Loan Amount Ranges"
    