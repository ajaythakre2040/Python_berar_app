from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.utils import timezone

from ems.models import TblEmpAddressDetails
from ems.serializers.emp_address_serializers import EmpAddressDetailsSerializer
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination


class EmpAddressDetailsListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        addresses = TblEmpAddressDetails.objects.filter(
            deleted_at__isnull=True
        ).order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(addresses, request)
        serializer = EmpAddressDetailsSerializer(page, many=True)
        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Address records retrieved successfully.",
            },
        )

    def post(self, request):
        serializer = EmpAddressDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Address details added successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to add address details.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmpAddressDetailsDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, employee_id):
        try:
            return TblEmpAddressDetails.objects.get(
                employee_id=employee_id, deleted_at__isnull=True
            )
        except TblEmpAddressDetails.DoesNotExist:
            raise NotFound(
                detail=f"Address record for employee ID {employee_id} not found."
            )

    def get(self, request, employee_id):
        address = self.get_object(employee_id)
        serializer = EmpAddressDetailsSerializer(address)
        return Response(
            {
                "success": True,
                "message": "Address details retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id):
        address = self.get_object(employee_id)
        serializer = EmpAddressDetailsSerializer(
            address, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Address details updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update address details.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, employee_id):
        address = self.get_object(employee_id)
        address.deleted_at = timezone.now()
        address.deleted_by = request.user.id
        address.save()
        return Response(
            {
                "success": True,
                "message": "Address details deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
