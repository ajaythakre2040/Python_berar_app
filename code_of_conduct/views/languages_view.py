from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from code_of_conduct.serializers.languages_serializer import LanguagesSerializer
from code_of_conduct.models.languages import Languages
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework import status
from django.utils import timezone
from rest_framework.exceptions import NotFound
from auth_system.utils.pagination import CustomPagination


# ✅ LanguagesListCreateView
class LanguagesListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)

        if search_query:
            enquiries = Languages.objects.filter(
                name__icontains=search_query, deleted_at__isnull=True
            ).order_by("id")
        else:
            enquiries = Languages.objects.filter(deleted_at__isnull=True).order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page_size or page:
            page_data = paginator.paginate_queryset(enquiries, request)
            serializer = LanguagesSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Languages types retrieved successfully (paginated).",
                },
            )
        else:
            serializer = LanguagesSerializer(enquiries, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Languages types retrieved successfully.",
                    "data": serializer.data,
                }
            )

    def post(self, request):
     serializer = LanguagesSerializer(data=request.data)
     if serializer.is_valid():
        try:
            language = serializer.save(created_by=request.user.id)
            response_serializer = LanguagesSerializer(language)
            return Response(
                {
                    "success": True,
                    "message": "Language Type Created Successfully.",
                    "data": response_serializer.data
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
            "message": "Failed to create language type.",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )



# ✅ LanguagesDetailView (⬅ OUTSIDE the ListCreateView class)
class LanguagesDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return Languages.objects.get(pk=pk, deleted_at__isnull=True)
        except Languages.DoesNotExist:
            raise NotFound(detail=f"Language type with id {pk} not found.")

    def get(self, request, pk):
        language = self.get_object(pk)
        serializer = LanguagesSerializer(language)
        return Response(
            {
                "success": True,
                "message": "Language type retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        language = self.get_object(pk)
        serializer = LanguagesSerializer(language, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Language type updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update language type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def delete(self, request, pk):
        languages = self.get_object(pk)
        languages.deleted_at = timezone.now()
        languages.deleted_by = request.user.id
        languages.save()

        # Return deleted brand info (optional)
        serializer = LanguagesSerializer(languages)
        return Response(
            {
                "success": True,
                "message": "Languages type deleted successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK,
        )
