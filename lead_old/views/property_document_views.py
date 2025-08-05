from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import IntegrityError

from auth_system.permissions.token_valid import IsTokenValid
from lead.models.property_document import PropertyDocument
from lead.serializers.property_document_serializer import PropertyDocumentSerializer
from auth_system.utils.pagination import CustomPagination


class PropertyDocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)

        if search_query:
            queryset = PropertyDocument.objects.filter(
                name__icontains=search_query, deleted_at__isnull=True
            )
        else:
            queryset = PropertyDocument.objects.filter(deleted_at__isnull=True)

        paginator = CustomPagination()
        page_data = paginator.paginate_queryset(queryset, request)
        serializer = PropertyDocumentSerializer(page_data, many=True)

        return paginator.get_custom_paginated_response(
            serializer.data,
            {"success": True, "message": "Property documents retrieved successfully"},
        )

    def post(self, request):
        serializer = PropertyDocumentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Property document created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "Property document with this name already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PropertyDocumentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return PropertyDocument.objects.get(pk=pk, deleted_at__isnull=True)
        except PropertyDocument.DoesNotExist:
            raise NotFound("Property document not found.")

    def get(self, request, pk):
        doc = self.get_object(pk)
        serializer = PropertyDocumentSerializer(doc)
        return Response(
            {
                "success": True,
                "message": "Property document retrieved successfully.",
                "data": serializer.data,
            }
        )

    def patch(self, request, pk):
        doc = self.get_object(pk)
        serializer = PropertyDocumentSerializer(doc, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Property document updated successfully.",
                    "data": serializer.data,
                }
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        doc = self.get_object(pk)
        doc.deleted_at = timezone.now()
        doc.deleted_by = request.user.id
        doc.save()
        return Response(
            {"success": True, "message": "Property document deleted successfully."}
        )
