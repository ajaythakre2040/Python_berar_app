from rest_framework import serializers
from code_of_conduct.models.deposit_agents_data import DepositAgentsData

class DepositAgentsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositAgentsData
        fields = '__all__'
