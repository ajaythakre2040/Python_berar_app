from rest_framework import serializers
from code_of_conduct.models.ras_data import RasData

class RasDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RasData
        fields = '__all__'
