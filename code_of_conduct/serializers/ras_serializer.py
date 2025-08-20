from rest_framework import serializers 
from  code_of_conduct.models.ras import Ras

class RasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ras
        fields = '__all__'
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        ]