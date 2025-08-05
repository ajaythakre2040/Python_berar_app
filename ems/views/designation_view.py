from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import IntegrityError

from auth_system.permissions.token_valid import IsTokenValid
from ems.models import TblDesignation
from ems.serializers.designation_serializers import TblDesignationSerializer
from auth_system.utils.pagination import CustomPagination
from django.db.models import Q

class TblDesignationListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get('search', '')  # ?search=manager jaisa query param

        designations = TblDesignation.objects.filter(deleted_at__isnull=True)

        if search_query:
            designations = designations.filter(
                Q(designation_name__icontains=search_query)
                | Q(designation_code__icontains=search_query)
                | Q(designation_priority__icontains=search_query)
                | Q(parent_designation_id__icontains=search_query)
            )

        designations = designations.order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(designations, request)
        serializer = TblDesignationSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Designations retrieved successfully.",
            },
        )

    def post(self, request):
        serializer = TblDesignationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Designation created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Designation creation failed due to duplicate entry.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {
                "success": False,
                "message": "Failed to create designation.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class TblDesignationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return TblDesignation.objects.get(pk=pk, deleted_at__isnull=True)
        except TblDesignation.DoesNotExist:
            raise NotFound(detail=f"Designation with id {pk} not found.")

    def get(self, request, pk):
        designation = self.get_object(pk)
        serializer = TblDesignationSerializer(designation)
        return Response(
            {
                "success": True,
                "message": "Designation retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        designation = self.get_object(pk)
        serializer = TblDesignationSerializer(
            designation, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Designation updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update designation.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        designation = self.get_object(pk)
        designation.deleted_at = timezone.now()
        designation.deleted_by = request.user.id
        designation.save()
        return Response(
            {
                "success": True,
                "message": "Designation deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ParentDesignationsView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        parent_designations = TblDesignation.objects.filter(
            parent_designation_id=0, deleted_at__isnull=True
        ).order_by("designation_priority")

        if not parent_designations.exists():
            return Response(
                {
                    "success": True,
                    "message": "No parent designations found.",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        serializer = TblDesignationSerializer(parent_designations, many=True)
        return Response(
            {
                "success": True,
                "message": "Parent designations retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
