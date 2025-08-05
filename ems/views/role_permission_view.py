from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.utils import timezone

from ems.models import RolePermission
from ems.serializers.role_serializer import RolePermissionSerializer
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination


class RolePermissionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        permissions = RolePermission.objects.filter(deleted_at__isnull=True).order_by(
            "id"
        )
        paginator = CustomPagination()
        page = paginator.paginate_queryset(permissions, request)
        serializer = RolePermissionSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Role permissions retrieved successfully.",
            },
        )

    def post(self, request):
        serializer = RolePermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Role permission created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create role permission.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class RolePermissionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return RolePermission.objects.get(pk=pk, deleted_at__isnull=True)
        except RolePermission.DoesNotExist:
            raise NotFound(detail=f"Role permission with ID {pk} not found.")

    def get(self, request, pk):
        permission = self.get_object(pk)
        serializer = RolePermissionSerializer(permission)
        return Response(
            {
                "success": True,
                "message": "Role permission retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        permission = self.get_object(pk)
        serializer = RolePermissionSerializer(
            permission, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Role permission updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update role permission.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        permission = self.get_object(pk)
        permission.deleted_at = timezone.now()
        permission.deleted_by = request.user.id
        permission.save()
        return Response(
            {"success": True, "message": "Role permission deleted successfully."},
            status=status.HTTP_200_OK,
        )
