from django.urls import path

from lead.views.nature_of_business_views import (
    NatureOfBusinessListCreateView,
    NatureOfBusinessDetailView,
)
from lead.views.product_type_views import (
    ProductTypeListCreateView,
    ProductTypeDetailView,
)
from lead.views.property_type_views import (
    PropertyTypeListCreateView,
    PropertyTypeDetailView,
)
from lead.views.property_document_views import (
    PropertyDocumentListCreateView,
    PropertyDocumentDetailView,
)
from lead.views.loan_amount_range_views import (
    LoanAmountRangeListCreateView,
    LoanAmountRangeDetailView,
)

urlpatterns = [

    path(
        "nature-of-businesses/",
        NatureOfBusinessListCreateView.as_view(),
        name="nature-of-business-list-create",
    ),
    path(
        "nature-of-businesses/<int:pk>/",
        NatureOfBusinessDetailView.as_view(),
        name="nature-of-business-detail",
    ),
    path(
        "product-types/",
        ProductTypeListCreateView.as_view(),
        name="product-type-list-create",
    ),
    path(
        "product-types/<int:pk>/",
        ProductTypeDetailView.as_view(),
        name="product-type-detail",
    ),
    path(
        "property-types/",
        PropertyTypeListCreateView.as_view(),
        name="property-type-list-create",
    ),
    path(
        "property-types/<int:pk>/",
        PropertyTypeDetailView.as_view(),
        name="property-type-detail",
    ),
    path(
        "property-documents/",
        PropertyDocumentListCreateView.as_view(),
        name="property-document-list-create",
    ),
    path(
        "property-documents/<int:pk>/",
        PropertyDocumentDetailView.as_view(),
        name="property-document-detail",
    ),
    path(
        "loan-amount-ranges/",
        LoanAmountRangeListCreateView.as_view(),
        name="loan-amount-range-list-create",
    ),
    path(
        "loan-amount-ranges/<int:pk>/",
        LoanAmountRangeDetailView.as_view(),
        name="loan-amount-range-detail",
    ),
]
