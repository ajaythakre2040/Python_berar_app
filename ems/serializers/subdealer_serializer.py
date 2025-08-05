from rest_framework import serializers
from ems.models import SubDealer, Dealer


class SubDealerSerializer(serializers.ModelSerializer):
    dealer_id = serializers.PrimaryKeyRelatedField(
        queryset=Dealer.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            "does_not_exist": "Selected dealer does not exist.",
            "incorrect_type": "Dealer ID must be a valid integer.",
        },
    )

    class Meta:
        model = SubDealer
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        ]
