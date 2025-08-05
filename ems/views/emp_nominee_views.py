from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.utils import timezone

from ems.models import TblEmpNomineeDetails
from ems.serializers.emp_nominee_serializers import TblEmpNomineeDetailsSerializer
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination


class EmpNomineeDetailsListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        nominees = TblEmpNomineeDetails.objects.filter(
            deleted_at__isnull=True
        ).order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(nominees, request)
        serializer = TblEmpNomineeDetailsSerializer(page, many=True)
        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Nominee records retrieved successfully.",
            },
        )

    def post(self, request):
        serializer = TblEmpNomineeDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Nominee details added successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to add nominee details.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmpNomineeDetailsDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, employee_id):
        try:
            return TblEmpNomineeDetails.objects.get(
                employee_id=employee_id, deleted_at__isnull=True
            )
        except TblEmpNomineeDetails.DoesNotExist:
            raise NotFound(
                detail=f"Nominee record for employee ID {employee_id} not found."
            )

    def get(self, request, employee_id):
        nominee = self.get_object(employee_id)
        serializer = TblEmpNomineeDetailsSerializer(nominee)
        return Response(
            {
                "success": True,
                "message": "Nominee details retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id):
        nominee = self.get_object(employee_id)
        serializer = TblEmpNomineeDetailsSerializer(
            nominee, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Nominee details updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update nominee details.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, employee_id):
        nominee = self.get_object(employee_id)
        nominee.deleted_at = timezone.now()
        nominee.deleted_by = request.user.id
        nominee.save()
        return Response(
            {
                "success": True,
                "message": "Nominee details deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class EmpNomineeDetailsDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, employee_id):
        try:
            return TblEmpNomineeDetails.objects.get(
                employee_id_id=employee_id, deleted_at__isnull=True
            )
        except TblEmpNomineeDetails.DoesNotExist:
            raise NotFound(
                detail=f"Nominee record for employee ID {employee_id} not found."
            )

    def get(self, request, employee_id):
        nominee = self.get_object(employee_id)
        serializer = TblEmpNomineeDetailsSerializer(nominee)
        return Response(
            {
                "success": True,
                "message": "Nominee details retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id):
        nominee = self.get_object(employee_id)
        serializer = TblEmpNomineeDetailsSerializer(
            nominee, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Nominee details updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update nominee details.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, employee_id):
        nominee = self.get_object(employee_id)
        nominee.deleted_at = timezone.now()
        nominee.deleted_by = request.user.id
        nominee.save()
        return Response(
            {
                "success": True,
                "message": "Nominee details deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
