from rest_framework import serializers
from code_of_conduct.models.dsa import Dsa

class DsaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dsa
        fields = '__all__'
