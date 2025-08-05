from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from auth_system.permissions.token_valid import IsTokenValid
from lead.models.nature_of_business import NatureOfBusiness
from lead.serializers.nature_of_business_serializer import NatureOfBusinessSerializer
from auth_system.utils.pagination import CustomPagination
from django.db import IntegrityError


class NatureOfBusinessListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)

        if search_query:
            business_types = NatureOfBusiness.objects.filter(
                name__icontains=search_query,
                deleted_at__isnull=True
            ).order_by("id")
        else:
            business_types = NatureOfBusiness.objects.filter(
                deleted_at__isnull=True
            ).order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get('page_size')
        page = request.query_params.get('page')

        if page_size or page:
            page_data = paginator.paginate_queryset(business_types, request)
            serializer = NatureOfBusinessSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Nature of businesses retrieved successfully (paginated).",
                },
            )
        else:
            serializer = NatureOfBusinessSerializer(business_types, many=True)
            return Response({
                "success": True,
                "message": "Nature of businesses retrieved successfully (all data, no pagination).",
                "data": serializer.data,
            })
    def post(self, request):
        serializer = NatureOfBusinessSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Nature of business created successfully.",
                       
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
                "message": "Failed to create nature of business.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class NatureOfBusinessDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return NatureOfBusiness.objects.get(pk=pk, deleted_at__isnull=True)
        except NatureOfBusiness.DoesNotExist:
            raise NotFound(detail=f"Nature of business with id {pk} not found.")

    def get(self, request, pk):
        obj = self.get_object(pk)
        serializer = NatureOfBusinessSerializer(obj)
        return Response(
            {
                "success": True,
                "message": "Nature of business retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        obj = self.get_object(pk)
        serializer = NatureOfBusinessSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Nature of business updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update nature of business.",
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
            {"success": True, "message": "Nature of business deleted successfully."},
            status=status.HTTP_200_OK,
        )
