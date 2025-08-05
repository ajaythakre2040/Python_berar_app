from rest_framework import serializers 
from  code_of_conduct.models.ras import Ras

class RasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ras
        fields = '__all__'