import requests
from rest_framework.response import Response
from rest_framework import status
from auth_system.utils.session_key_utils import get_mis_auth_headers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from cms.utils.mis_helpers import call_mis_api
from api_endpoints import (
    CUSTOMER_GET_ALL_URL,
    CUSTOMER_COUNT_URL,
    CUSTOMER_SEARCH_URL,
    CUSTOMER_GET_BY_ACCOUNT_URL,
)


class AllCustomersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        params = request.query_params 
        return call_mis_api(request, CUSTOMER_GET_ALL_URL, params=params, timeout=30)


class CustomerCountView(APIView):

    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        return call_mis_api(request, CUSTOMER_COUNT_URL)


class CustomerFlexibleSearchView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        params = request.query_params
        return call_mis_api(request, CUSTOMER_SEARCH_URL, params=params, timeout=30)


class CustomerByAccountNumberView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        account_number = request.query_params.get("account_number")

        if not account_number:
            return Response(
                {"detail": "account_number is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        params = {"loanAccount": account_number}
        return call_mis_api(
            request, CUSTOMER_GET_BY_ACCOUNT_URL, params=params, timeout=30
        )
