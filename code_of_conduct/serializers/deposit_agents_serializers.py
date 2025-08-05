from rest_framework import serializers
from code_of_conduct.models.deposit_agents import DepositAgents

class DepositAgentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositAgents
        fields = '__all__'
