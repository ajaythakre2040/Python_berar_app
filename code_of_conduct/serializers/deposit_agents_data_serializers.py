from rest_framework import serializers
from code_of_conduct.models.deposit_agents_data import DepositAgentsData

class DepositAgentsDataSerializer(serializers.ModelSerializer):
    class Meta:
         model = DepositAgentsData
         fields = '__all__'
         read_only_fields = [
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        ]