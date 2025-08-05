from rest_framework import serializers
from code_of_conduct.models.dsa_data import DsaData

class DsaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DsaData
        fields = '__all__'
