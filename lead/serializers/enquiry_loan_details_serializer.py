from rest_framework import serializers
from lead.models.enquiry_loan_details import EnquiryLoanDetails



class EnquiryLoanDetailsSerializer(serializers.ModelSerializer):
    loan_type_display = serializers.CharField(source="loan_type.name", read_only=True)
    loan_amount_range_display = serializers.SerializerMethodField()
    property_type_display = serializers.CharField(source="property_type.name", read_only=True)
    enquiry_display = serializers.SerializerMethodField()
    loan_required_on_display = serializers.SerializerMethodField()
    enquiry_type_display = serializers.SerializerMethodField()
    end_user_display = serializers.SerializerMethodField()

    enquiry = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EnquiryLoanDetails
        fields = [
            "id",
            "loan_type",                
            "loan_type_display",        
            "loan_amount_range",
            "loan_amount_range_display",
            "property_type",
            "property_type_display",
            "enquiry",                
            "enquiry_display",
            "property_document_type",
            "sale_deed_number",
            "agreement_sell_number",
            "property_document_number",
            "akhive_patrika",
            "property_value",
            "loan_required_on",
            "loan_required_on_display",  # ✅ FIX: Added here
            "vehicle_registration_number",
            "income_document",
            "followup_pickup_date",
            "enquiry_type",
            "enquiry_type_display",
            "remark",
            "end_user",
            "end_user_display",   # ✅ include it
        ]
        read_only_fields = (
            "enquiry",
            "enquiry_display",
            "loan_type_display",
            "property_type_display",
            "loan_amount_range_display",
            "enquiry_type_display",
            "loan_required_on_display",
            "end_user_display",
        )

    def get_loan_amount_range_display(self, obj):
        if obj.loan_amount_range:
            return f"{obj.loan_amount_range.loan_amount_from} - {obj.loan_amount_range.loan_amount_to}"
        return None

    def get_enquiry_display(self, obj):
        return str(obj.enquiry) if obj.enquiry else None

    def get_enquiry_type_display(self, obj):
        return obj.get_enquiry_type_display() if obj.enquiry_type is not None else None
    
    def get_loan_required_on_display(self, obj):
        return obj.get_loan_required_on_display()
        
    def get_end_user_display(self, obj):
        return str(obj.end_user) if obj.end_user else None