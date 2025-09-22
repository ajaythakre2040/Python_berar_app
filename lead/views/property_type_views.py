from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from auth_system.permissions.token_valid import IsTokenValid
from lead.models.property_type import PropertyType
from lead.serializers.property_type_serializer import PropertyTypeSerializer
from auth_system.utils.pagination import CustomPagination
from django.db import IntegrityError


class PropertyTypeListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)

        if search_query:
            property_types = PropertyType.objects.filter(
                name__icontains=search_query,
                deleted_at__isnull=True
            ).order_by("-id")
        else:
            property_types = PropertyType.objects.filter(
                deleted_at__isnull=True
            ).order_by("-id")

        paginator = CustomPagination()
        page_size = request.query_params.get('page_size')
        page = request.query_params.get('page')

        if page_size or page:
            page_data = paginator.paginate_queryset(property_types, request)
            serializer = PropertyTypeSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Property types retrieved successfully (paginated).",
                },
            )
        else:
            serializer = PropertyTypeSerializer(property_types, many=True)
            return Response({
                "success": True,
                "message": "Property types retrieved successfully (all data, no pagination).",
                "data": serializer.data,
            })

    def post(self, request):
        serializer = PropertyTypeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Property type created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Creation failed due to duplicate entry.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {
                "success": False,
                "message": "Failed to create property type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PropertyTypeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return PropertyType.objects.get(pk=pk, deleted_at__isnull=True)
        except PropertyType.DoesNotExist:
            raise NotFound(detail=f"Property type with id {pk} not found.")

    def get(self, request, pk):
        obj = self.get_object(pk)
        serializer = PropertyTypeSerializer(obj)
        return Response(
            {
                "success": True,
                "message": "Property type retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        obj = self.get_object(pk)
        serializer = PropertyTypeSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Property type updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update property type.",
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
            {"success": True, "message": "Property type deleted successfully."},
            status=status.HTTP_200_OK,
        )
