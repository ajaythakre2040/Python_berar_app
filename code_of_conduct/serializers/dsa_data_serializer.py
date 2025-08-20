from rest_framework import serializers
from code_of_conduct.models.dsa_data import DsaData

class DsaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DsaData
        fields = '__all__'
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        ]