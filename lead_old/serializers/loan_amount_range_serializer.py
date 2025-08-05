from rest_framework import serializers
from ..models.loan_amount_range import LoanAmountRange


class LoanAmountRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanAmountRange
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
