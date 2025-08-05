from rest_framework import serializers

from ..models.languages import Languages


class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        # fields = "__all__"
        exclude = ('created_by', 'updated_by', 'deleted_by', 'created_at', 'updated_at', 'deleted_at')

        # read_only_fields = (
        #     "created_by",
        #     "updated_by",
        #     "deleted_by",
        #     "created_at",
        #     "updated_at",
        #     "deleted_at",
        # )
# 