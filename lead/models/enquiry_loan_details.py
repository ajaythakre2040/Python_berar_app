from django.db import models
from lead.models.enquiry import Enquiry
from lead.models.product_type import ProductType
from lead.models.loan_amount_range import LoanAmountRange
from lead.models.property_type import PropertyType
from lead.models.property_document import PropertyDocument
from django.utils import timezone
from constants import ENQUIRY_TYPE_CHOICES , TYPE_LOAN_REQUIRED_ON_CHOICES
from lead.models.enquiry_end_user  import EnquiryEnduser

class EnquiryLoanDetails(models.Model):

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="enquiry_loan_details")

    loan_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, blank=True)
    loan_amount_range = models.ForeignKey(LoanAmountRange, on_delete=models.SET_NULL, null=True, blank=True)

    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, blank=True)
    property_document_type = models.ForeignKey(PropertyDocument, on_delete=models.SET_NULL, null=True, blank=True)
    
    sale_deed_number = models.CharField(max_length=100, null=True, blank=True)
    agreement_sell_number = models.CharField(max_length=100, null=True, blank=True)
    property_document_number = models.CharField(max_length=100, null=True, blank=True)
    akhive_patrika = models.CharField(max_length=100, null=True, blank=True)

    property_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    loan_required_on = models.IntegerField(choices=TYPE_LOAN_REQUIRED_ON_CHOICES, null=True, blank=True)

    vehicle_registration_number = models.CharField(max_length=20, null=True, blank=True)

    income_document = models.CharField(max_length=255, null=True, blank=True)
    followup_pickup_date = models.DateField(null=True, blank=True)

    enquiry_type = models.IntegerField(choices=ENQUIRY_TYPE_CHOICES, null=True, blank=True)

    remark = models.TextField(null=True, blank=True)

    end_user = models.ForeignKey(
        EnquiryEnduser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None  
    )
    
    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=None)

    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Loan {self.id} | {self.enquiry.id} | {self.loan_type.name if self.loan_type else 'N/A'}"
    class Meta:
        db_table = "lead_enquiry_load_details"  # ✅ Custom table name
