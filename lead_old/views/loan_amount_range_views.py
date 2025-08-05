

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import IntegrityError

from auth_system.permissions.token_valid import IsTokenValid
from lead.models.loan_amount_range import LoanAmountRange
from lead.serializers.loan_amount_range_serializer import LoanAmountRangeSerializer
from auth_system.utils.pagination import CustomPagination


class LoanAmountRangeListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)

        if search_query:
            loan_ranges = LoanAmountRange.objects.filter(
                deleted_at__isnull=True,
                minimum_loan__icontains=search_query,  
            ).order_by("id")
        else:
            loan_ranges = LoanAmountRange.objects.filter(
                deleted_at__isnull=True
            ).order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page_size or page:
            page_data = paginator.paginate_queryset(loan_ranges, request)
            serializer = LoanAmountRangeSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Loan amount ranges retrieved successfully (paginated).",
                },
            )
        else:
            serializer = LoanAmountRangeSerializer(loan_ranges, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Loan amount ranges retrieved successfully (all data, no pagination).",
                    "data": serializer.data,
                }
            )

    def post(self, request):
        serializer = LoanAmountRangeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Loan amount range created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Creation failed due to integrity error.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {
                "success": False,
                "message": "Failed to create loan amount range.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoanAmountRangeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return LoanAmountRange.objects.get(pk=pk, deleted_at__isnull=True)
        except LoanAmountRange.DoesNotExist:
            raise NotFound(detail=f"Loan amount range with id {pk} not found.")

    def get(self, request, pk):
        obj = self.get_object(pk)
        serializer = LoanAmountRangeSerializer(obj)
        return Response(
            {
                "success": True,
                "message": "Loan amount range retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        obj = self.get_object(pk)
        serializer = LoanAmountRangeSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Loan amount range updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update loan amount range.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.deleted_at = timezone.now()
        obj.deleted_by = request.user.id
        obj.save()
        return Response(
            {"success": True, "message": "Loan amount range deleted successfully."},
            status=status.HTTP_200_OK,
        )
