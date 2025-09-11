from rest_framework import serializers
from lead.models.enquiry import Enquiry
from lead.models.enquiry_address import EnquiryAddress
from lead.models.enquiry_loan_details import EnquiryLoanDetails
from lead.models.enquiry_verifications import EnquiryVerification
from lead.models.enquiry_images import EnquiryImages
from lead.models.enquiry_selfie import EnquirySelfie
from ems.models.emp_basic_profile import TblEmpBasicProfile


class EnquiryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryAddress
        exclude = ("created_by", "updated_by", "deleted_by", "created_at", "updated_at", "deleted_at")

class EnquiryLoanDetailsSerializer(serializers.ModelSerializer):
    loan_type_display = serializers.SerializerMethodField()
    loan_amount_range_display = serializers.SerializerMethodField()
    property_type_display = serializers.SerializerMethodField()
    property_document_type_display = serializers.SerializerMethodField()
    loan_required_on_display = serializers.SerializerMethodField()
    enquiry_type_display = serializers.SerializerMethodField()
    end_user_display = serializers.SerializerMethodField()


    class Meta:
        model = EnquiryLoanDetails
        exclude = ("created_by", "updated_by", "deleted_by", "created_at", "updated_at", "deleted_at")

    def get_loan_type_display(self, obj):
        return obj.loan_type.name if obj.loan_type else None

    def get_loan_amount_range_display(self, obj):
        return str(obj.loan_amount_range) if obj.loan_amount_range else None

    def get_property_type_display(self, obj):
        return obj.property_type.name if obj.property_type else None

    def get_property_document_type_display(self, obj):
        return obj.property_document_type.name if obj.property_document_type else None
    
    def get_enquiry_type_display(self, obj):
        return obj.get_enquiry_type_display() if obj.enquiry_type is not None else None
    
    def get_loan_required_on_display(self, obj):
        return obj.get_loan_required_on_display()
    
    def get_end_user_display(self, obj):
        return str(obj.end_user) if obj.end_user else None
    

class EnquiryVerificationSerializer(serializers.ModelSerializer):
    mobile_status_display = serializers.SerializerMethodField()
    email_status_display = serializers.SerializerMethodField()

    class Meta:
        model = EnquiryVerification
        exclude = ("created_by", "updated_by", "deleted_by", "created_at", "updated_at", "deleted_at")

    def get_mobile_status_display(self, obj):
        return obj.get_mobile_status_display() if obj.mobile_status is not None else None

    def get_email_status_display(self, obj):
        return obj.get_email_status_display() if obj.email_status is not None else None


class EnquiryImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryImages
        exclude = ("created_by", "updated_by", "deleted_by", "created_at", "updated_at", "deleted_at")

class EnquirySelfieSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquirySelfie
        exclude = ("created_by", "updated_by", "deleted_by", "created_at", "updated_at", "deleted_at")

class EnquirySerializer(serializers.ModelSerializer):
    loan_type_display = serializers.SerializerMethodField()
    occupation_display = serializers.SerializerMethodField()
    is_status_display = serializers.SerializerMethodField()
    is_steps_display = serializers.SerializerMethodField()
    nature_of_business_display = serializers.SerializerMethodField()

    created_by = serializers.IntegerField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    created_by_code = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()   # ✅ instead of IntegerField


    enquiry_addresses = EnquiryAddressSerializer(many=True, read_only=True)
    enquiry_loan_details = EnquiryLoanDetailsSerializer(many=True, read_only=True)
    enquiry_verification = EnquiryVerificationSerializer(read_only=True)
    enquiry_images = EnquiryImagesSerializer(many=True, read_only=True)
    enquiry_selfies = EnquirySelfieSerializer(many=True, read_only=True)

    class Meta:
        model = Enquiry
        fields = [
            "id", "name", "mobile_number", "lan_number",
            "loan_type", "loan_type_display",
            "occupation", "occupation_display",
            "employer_name", "number_of_years_service",
            "official_contact_number", "nature_of_service", "monthly_income",
            "business_name", "business_place", "business_contact_number",
            "nature_of_business","nature_of_business_display", "income", "interested", "kyc_collected",
            "kyc_document", "kyc_number", "is_status","is_status_display", "is_steps","is_steps_display",
            "enquiry_addresses", "enquiry_loan_details",
            "enquiry_verification", "enquiry_images", "enquiry_selfies","created_by", "created_by_name", "created_by_code","created_at"
        ]

    def get_loan_type_display(self, obj):
        return obj.loan_type.name if obj.loan_type else None

    def get_occupation_display(self, obj):
        return obj.get_occupation_display() if obj.occupation else None

    def get_is_status_display(self, obj):
        return obj.get_is_status_display() if obj.is_status is not None else None

    def get_is_steps_display(self, obj):
        return obj.get_is_steps_display() if obj.is_steps is not None else None
    
    def get_nature_of_business_display(self, obj):
        return obj.nature_of_business.name if obj.nature_of_business else None
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            emp = TblEmpBasicProfile.objects.filter(id=obj.created_by).first()
            return emp.name if emp else None
        return None

    def get_created_by_code(self, obj):
        if obj.created_by:
            emp = TblEmpBasicProfile.objects.filter(id=obj.created_by).first()
            return emp.employee_code if emp else None
        return None
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d") if obj.created_at else None