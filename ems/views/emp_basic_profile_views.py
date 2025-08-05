from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django.db.models import Q
from ems.models.emp_basic_profile import TblEmpBasicProfile
from ems.serializers.emp_basic_profile_serializers import (
    EmpBasicProfileSerializer,
    FullEmployeeProfileSerializer,
)
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination


class EmpBasicProfileListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get('search', '').strip()

        queryset = TblEmpBasicProfile.objects.filter(deleted_at__isnull=True)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(employee_code__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(mobile_number__icontains=search_query) |
                Q(gender__icontains=search_query)
            )

        queryset = queryset.order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = FullEmployeeProfileSerializer(page, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Employee profiles retrieved successfully.",
                },
            )

        serializer = FullEmployeeProfileSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "message": "Employee profiles retrieved (no pagination).",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    def post(self, request):
        serializer = EmpBasicProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Employee profile created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmpBasicProfileDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return TblEmpBasicProfile.objects.get(pk=pk, deleted_at__isnull=True)
        except TblEmpBasicProfile.DoesNotExist:
            raise NotFound("Employee not found.")

    def get(self, request, pk):
        employee = self.get_object(pk)
        serializer = FullEmployeeProfileSerializer(employee)
        return Response(
            {
                "success": True,
                "message": "Employee full profile retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmpBasicProfileSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_at=timezone.now(), updated_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Employee profile updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Update failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmpBasicProfileSerializer(
            employee, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(updated_at=timezone.now(), updated_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Employee profile partially updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Partial update failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        employee = self.get_object(pk)
        employee.deleted_at = timezone.now()
        employee.deleted_by = request.user.id
        employee.save()
        return Response(
            {
                "success": True,
                "message": "Employee profile deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
