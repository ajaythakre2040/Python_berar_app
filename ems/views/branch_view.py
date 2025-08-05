from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from auth_system.permissions.token_valid import IsTokenValid
from ems.models import TblBranch
from ems.serializers import TblBranchSerializer
from auth_system.utils.pagination import CustomPagination
from django.db import IntegrityError
from django.db.models import Q

class TblBranchListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get('search', '')  # URL se ?search=xyz le rahe hain

        branches = TblBranch.objects.filter(deleted_at__isnull=True)

        if search_query:
            branches = branches.filter(
                Q(branch_name__icontains=search_query) |
                Q(branch_code__icontains=search_query) |
                Q(branch_id__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(mobile_number__icontains=search_query)
            )

        branches = branches.order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(branches, request)
        serializer = TblBranchSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Branches retrieved successfully.",
            },
        )

    def post(self, request):
        serializer = TblBranchSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Branch created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Branch creation failed due to duplicate entry.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
        {
            "success": False,
            "message": "Failed to create branch.",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


class TblBranchDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return TblBranch.objects.get(pk=pk, deleted_at__isnull=True)
        except TblBranch.DoesNotExist:
            raise NotFound(detail=f"Branch with id {pk} not found.")

    def get(self, request, pk):
        branch = self.get_object(pk)
        serializer = TblBranchSerializer(branch)
        return Response(
            {
                "success": True,
                "message": "Branch retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):  
        branch = self.get_object(pk)
        serializer = TblBranchSerializer(
            branch, data=request.data, partial=True
        )  
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Branch updated successfully (partial update).",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update branch.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        branch = self.get_object(pk)
        branch.deleted_at = timezone.now()
        branch.deleted_by = request.user.id
        branch.save()
        return Response(
            {"success": True, "message": "Branch deleted successfully."},
            status=status.HTTP_200_OK,
        )
