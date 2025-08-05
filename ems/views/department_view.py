from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import IntegrityError

from auth_system.permissions.token_valid import IsTokenValid
from ems.models.department import TblDepartment
from ems.serializers.department_serializers import TblDepartmentSerializer
from auth_system.utils.pagination import CustomPagination
from django.db.models import Q

class TblDepartmentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get('search', '')  

        departments = TblDepartment.objects.filter(deleted_at__isnull=True)

        if search_query:
            departments = departments.filter(
                Q(department_name__icontains=search_query)
                | Q(department_email=search_query)
            )

        departments = departments.order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(departments, request)
        serializer = TblDepartmentSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Departments retrieved successfully.",
            },
        )
    def post(self, request):
        serializer = TblDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Department created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Department creation failed due to duplicate entry.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "success": False,
                "message": "Failed to create department.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class TblDepartmentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return TblDepartment.objects.get(pk=pk, deleted_at__isnull=True)
        except TblDepartment.DoesNotExist:
            raise NotFound(detail=f"Department with id {pk} not found.")

    def get(self, request, pk):
        department = self.get_object(pk)
        serializer = TblDepartmentSerializer(department)
        return Response(
            {
                "success": True,
                "message": "Department retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):  
        department = self.get_object(pk)
        serializer = TblDepartmentSerializer(
            department, data=request.data, partial=True
        )  
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Department updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update department.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        department = self.get_object(pk)
        department.deleted_at = timezone.now()
        department.deleted_by = request.user.id
        department.save()
        return Response(
            {
                "success": True,
                "message": "Department deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
