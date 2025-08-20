from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.utils import timezone

from ems.models import TblEmpBankDetails
from ems.serializers.emp_bank_serializers import TblEmpBankDetailsSerializer


from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination


class EmpBankDetailsListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
  
    def get(self, request):
        banks = TblEmpBankDetails.objects.filter(deleted_at__isnull=True).order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(banks, request)
        serializer = TblEmpBankDetailsSerializer(page, many=True)
        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Bank records retrieved successfully.",
            },
        )

    def post(self, request):
        serializer = TblEmpBankDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Bank details added successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to add bank details.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmpBankDetailsDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, employee_id):
        try:
            return TblEmpBankDetails.objects.get(
                employee_id=employee_id, deleted_at__isnull=True
            )
        except TblEmpBankDetails.DoesNotExist:
            raise NotFound(
                detail=f"Bank record for employee ID {employee_id} not found."
            )

    def get(self, request, employee_id):
        bank = self.get_object(employee_id)
        serializer = TblEmpBankDetailsSerializer(bank)
        return Response(
            {
                "success": True,
                "message": "Bank details retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id):
        bank = self.get_object(employee_id)
        serializer = TblEmpBankDetailsSerializer(bank, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Bank details updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update bank details.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, employee_id):
        bank = self.get_object(employee_id)
        bank.deleted_at = timezone.now()
        bank.deleted_by = request.user.id
        bank.save()
        return Response(
            {
                "success": True,
                "message": "Bank details deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
