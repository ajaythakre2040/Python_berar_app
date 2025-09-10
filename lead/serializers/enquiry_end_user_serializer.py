from rest_framework import serializers
from ..models.enquiry_end_user import EnquiryEnduser

class EnquiryEndUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryEnduser
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        extra_kwargs = {
            "title": {"validators": []}, 
        }

    def validate_title(self, value):
        qs = EnquiryEnduser.objects.filter(title=value, deleted_at__isnull=True)
        if self.instance:  
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("An active end user with this title already exists.")
        return value

