
from django.db import models
from lead.models.product_type import ProductType
from django.utils import timezone
from constants import OCCUPATION_CHOICES,SALARIED, SELF_EMPLOYED
from constants import PercentageStatus
from constants import EnquiryStatus

class Enquiry(models.Model):

    OCCUPATION_CHOICES = (
        (SALARIED, 'Salaried'),
        (SELF_EMPLOYED, 'Self-Employed'),
    )

    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    lan_number = models.CharField(max_length=15, null=True, blank=True)

    loan_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, blank=True)
    
    occupation = models.CharField(max_length=100, choices=OCCUPATION_CHOICES, null=False)
    employer_name = models.CharField(max_length=255, null=True, blank=True)
    number_of_years_service = models.IntegerField(null=True, blank=True)
    official_contact_number = models.CharField(max_length=15, null=True, blank=True)
    nature_of_service = models.CharField(max_length=100, null=True, blank=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_place = models.CharField(max_length=255, null=True, blank=True)
    business_contact_number = models.CharField(max_length=15, null=True, blank=True)
    nature_of_business = models.CharField(max_length=100, null=True, blank=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    interested = models.BooleanField(default=False)
    kyc_collected = models.BooleanField(default=False)
    kyc_document = models.CharField(max_length=255, null=True, blank=True)
    kyc_number = models.CharField(max_length=50, null=True, blank=True)
    is_steps = models.IntegerField(choices=PercentageStatus.choices, default=PercentageStatus.ENQUIRY_BASIC)    
    is_status = models.IntegerField(choices=EnquiryStatus.choices,default=EnquiryStatus.DRAFT)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.name} -{self.mobile_number}"
