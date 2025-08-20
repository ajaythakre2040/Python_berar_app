from rest_framework import serializers
from code_of_conduct.models.questions import Questions

class QuestionsSerializer(serializers.ModelSerializer):
    type_constant_display = serializers.CharField(source='get_type_constant_display', read_only=True)

    class Meta:
        model = Questions
        fields = '__all__'
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "deleted_by",
            "deleted_at",
        ]