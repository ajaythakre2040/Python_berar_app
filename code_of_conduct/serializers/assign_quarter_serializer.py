from rest_framework import serializers 
from  code_of_conduct.models.assign_quarter import AssignQuarter

class AssignQuarterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignQuarter
        fields = '__all__'