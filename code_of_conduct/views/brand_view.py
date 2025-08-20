from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from code_of_conduct.serializers.brand_serializer import BrandSerializer
from code_of_conduct.models.brand import Brand
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework import status
from django.utils import timezone
from rest_framework.exceptions import NotFound
from auth_system.utils.pagination import CustomPagination


class BrandListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)

        if search_query:
            enquiries = Brand.objects.filter(
                name__icontains=search_query, deleted_at__isnull=True
            ).order_by("id")
        else:
            enquiries = Brand.objects.filter(deleted_at__isnull=True).order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page_size or page:
            page_data = paginator.paginate_queryset(enquiries, request)
            serializer = BrandSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Brand types retrieved successfully (paginated).",
                },
            )
        else:
            serializer = BrandSerializer(enquiries, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Brand types retrieved successfully.",
                    "data": serializer.data,
                }
            )

    def post(self, request):
     serializer = BrandSerializer(data=request.data)
     if serializer.is_valid():
        try:
            brand = serializer.save(created_by=request.user.id)  # object mil gaya
            response_serializer = BrandSerializer(brand)         # usko dobara serialize karo
            return Response(
                {
                    "success": True,
                    "message": "Brand Type Created Successfully.",
                    "data": response_serializer.data              # yaha return ho raha hai id, name, etc.
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
            "message": "Failed to create Brand type.",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
       )



class BrandDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return Brand.objects.get(pk=pk, deleted_at__isnull=True)
        except Brand.DoesNotExist:
            raise NotFound(detail=f"Brand type with id {pk} not found.")

    def get(self, request, pk):
        language = self.get_object(pk)
        serializer = BrandSerializer(language)
        return Response(
            {
                "success": True,
                "message": "Brand type retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        brand = self.get_object(pk)
        serializer = BrandSerializer(brand, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Brand type updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update brand type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        brand = self.get_object(pk)
        brand.deleted_at = timezone.now()
        brand.deleted_by = request.user.id
        brand.save()

        # Return deleted brand info (optional)
        serializer = BrandSerializer(brand)
        return Response(
            {
                "success": True,
                "message": "Brand type deleted successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK,
        )
