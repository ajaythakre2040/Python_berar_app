from django.urls import path
from cms.views.customer_view import (
    AllCustomersView,
    CustomerByAccountNumberView,
    CustomerCountView,
    CustomerFlexibleSearchView,
)

urlpatterns = [
    path("customers/", AllCustomersView.as_view(), name="all-customers"),
    path("customers/count/", CustomerCountView.as_view(), name="customer-count"),
    path(
        "customers/search/",
        CustomerFlexibleSearchView.as_view(),
        name="customer-search",
    ),
    path("customers/getBy-account-number/", CustomerByAccountNumberView.as_view()),
]
