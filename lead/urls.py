from django.urls import path

from lead.views.nature_of_business_views import NatureOfBusinessListCreateView, NatureOfBusinessDetailView
from lead.views.product_type_views import ProductTypeListCreateView, ProductTypeDetailView
from lead.views.property_type_views import PropertyTypeListCreateView, PropertyTypeDetailView
from lead.views.property_document_views import PropertyDocumentListCreateView, PropertyDocumentDetailView
from lead.views.loan_amount_range_views import LoanAmountRangeListCreateView, LoanAmountRangeDetailView

from lead.views.enquirey_view import EnquiryListCreateAPIView, EnquiryDetailView, EnquiryExistingDataAPIView
from lead.views.enquiry_address_view import EnquiryAddressCreateAPIView
from lead.views.enquiry_loan_details_view import EnquiryLoanDetailsCreateAPIView
from lead.views.enquiry_images_view import EnquiryImagesCreateAPIView, EnquiryImagesGetAPIView,EnquiryImagesDeleteAPIView,EnquiryImagesListAPIView
from lead.views.enquiry_selfie_view import EnquirySelfieCreateAPIView, EnquirySelfieReplaceAPIView
from lead.views.enquiry_verification_view import EnquiryVerificationCreateAPIView , otpVerificationAPIView,EnquiryVerificationCompleteAPIView

from lead.views.configruation_view import ConfigurationListCreateAPIView, ConfigurationDetailAPIView

from lead.views.enquiry_followup import EnquiryFollowUpCountAPIView, FollowUpUpdateAPIView, ActiveEnquiriesAPIView,ClosedEnquiriesAPIView,ReopenEnquiryView,AllCountAPIView, ThisMonthEnquiryListAPIView, TodayEnquiryListAPIView

from lead.views.enquiry_lead_assign_view import LeadAssignView, GetBranchAndFilterEmployeesAPIView, GetAssigned



urlpatterns = [

    path("nature-of-businesses/", NatureOfBusinessListCreateView.as_view(), name="nature-of-business-list-create"),
    path("nature-of-businesses/<int:pk>/", NatureOfBusinessDetailView.as_view(), name="nature-of-business-detail"),

    path("product-types/", ProductTypeListCreateView.as_view(), name="product-type-list-create"),
    path("product-types/<int:pk>/", ProductTypeDetailView.as_view(), name="product-type-detail"),

    path("property-types/", PropertyTypeListCreateView.as_view(), name="property-type-list-create"),
    path("property-types/<int:pk>/", PropertyTypeDetailView.as_view(), name="property-type-detail"),

    path("property-documents/", PropertyDocumentListCreateView.as_view(), name="property-document-list-create"),
    path("property-documents/<int:pk>/", PropertyDocumentDetailView.as_view(), name="property-document-detail"),

    path("loan-amount-ranges/", LoanAmountRangeListCreateView.as_view(), name="loan-amount-range-list-create"),
    path("loan-amount-ranges/<int:pk>/", LoanAmountRangeDetailView.as_view(), name="loan-amount-range-detail"),

    path("enquiries/", EnquiryListCreateAPIView.as_view(), name="enquiry-list-create"),
    path("enquiries/<int:pk>/", EnquiryDetailView.as_view(), name="enquiry-detail"),

    path("enquiries/<int:enquiry_id>/address/", EnquiryAddressCreateAPIView.as_view(), name="enquiry-address-create"),
    path("enquiries/<int:enquiry_id>/loan_details/", EnquiryLoanDetailsCreateAPIView.as_view(), name="enquiry-loan-details-create"),

    path("enquiries/<int:enquiry_id>/images/", EnquiryImagesCreateAPIView.as_view(), name="enquiry-images-create"),
    path("enquiries/<int:enquiry_id>/images/<int:image_id>/", EnquiryImagesDeleteAPIView.as_view(), name="enquiry-images-delete"),

    path("enquiries/<int:enquiry_id>/images/<int:image_id>", EnquiryImagesGetAPIView.as_view(), name="enquiry-images-get"),
    path("enquiries/<int:enquiry_id>/images", EnquiryImagesListAPIView.as_view(), name="enquiry-images-get-all"),

    path("enquiries/<int:enquiry_id>/selfie/", EnquirySelfieCreateAPIView.as_view(), name="enquiry-selfie-create"),
    path("enquiries/<int:enquiry_id>/selfie/<int:selfie_id>/", EnquirySelfieReplaceAPIView.as_view(), name="enquiry-selfie-replace"),

    path("enquiries/<int:enquiry_id>/verification/", EnquiryVerificationCreateAPIView.as_view(), name="enquiry-verification-create"),
    path("enquiries/<int:enquiry_id>/otp_verification/", otpVerificationAPIView.as_view(), name="opt-verification"),

    path("enquiries/<int:enquiry_id>/verification/complete/", EnquiryVerificationCompleteAPIView.as_view(), name="enquiry-verification-complete"),

    # path("enquiries/<int:enquiry_id>/skip_verification/", SkipMobileOtpAPIView.as_view(), name="skip-verification"),
    path("enquiries/existing-data/", EnquiryExistingDataAPIView.as_view(), name="enquiry-existing-data"),

    path("configruation/", ConfigurationListCreateAPIView.as_view(), name="configruation-list-create"),
    path("configruation/<int:pk>/", ConfigurationDetailAPIView.as_view(), name="configruation-detail"),

    path('enquiries/followup/', EnquiryFollowUpCountAPIView.as_view(), name='enquiry-followup'),
    path('enquiries/followup/update/', FollowUpUpdateAPIView.as_view(), name='enquiry-followup-update'),

    path("enquiries/active/", ActiveEnquiriesAPIView.as_view(), name="active-enquiries"),
    path("enquiries/closed/", ClosedEnquiriesAPIView.as_view(), name="closed-enquiries"),

    path("enquiries/<int:enquiry_id>/reopen/", ReopenEnquiryView.as_view(), name="reopen-enquiry"),
    path("enquiries/all_counts/", AllCountAPIView.as_view(), name="lead-assign"),

    path("enquiries/today/", TodayEnquiryListAPIView.as_view(), name="enquiries-today"),
    path("enquiries/this-month/", ThisMonthEnquiryListAPIView.as_view(), name="enquiries-this-month"),

    path("enquiries/lead_assign/branch-employees/", GetBranchAndFilterEmployeesAPIView.as_view(), name="branch-employees"),
    path("enquiries/<int:enquiry_id>/lead_assign/", LeadAssignView.as_view(), name="lead-assign"),

    
    path("enquiries/assigned_lead/", GetAssigned.as_view(), name="lead-assign"),

    
]
