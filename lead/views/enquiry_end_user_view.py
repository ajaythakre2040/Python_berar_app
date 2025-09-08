from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from auth_system.permissions.token_valid import IsTokenValid
from lead.models.enquiry_end_user import EnquiryEnduser
from lead.serializers.enquiry_end_user_serializer import EnquiryEndUserSerializer
from auth_system.utils.pagination import CustomPagination
from django.db import IntegrityError


class EnquiryEndUserCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        """
        Retrieve end users with optional search and pagination.
        Pagination is applied by default with optional page/page_size query params.
        """
        search_query = request.query_params.get("search", None)

        queryset = EnquiryEnduser.objects.filter(deleted_at__isnull=True).order_by("id")
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        paginator = CustomPagination()
        page_data = paginator.paginate_queryset(queryset, request)
        serializer = EnquiryEndUserSerializer(page_data, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "End users retrieved successfully.",
            },
        )

    def post(self, request):
        """
        Create a new end user.
        Handles duplicate entries gracefully.
        """
        serializer = EnquiryEndUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "End user created successfully.",
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
                "message": "Failed to create End user.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class EnquiryEnduserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return EnquiryEnduser.objects.get(pk=pk, deleted_at__isnull=True)
        except EnquiryEnduser.DoesNotExist:
            raise NotFound(detail=f"End user with id {pk} not found.")

    def get(self, request, pk):
        obj = self.get_object(pk)
        serializer = EnquiryEndUserSerializer(obj)
        return Response(
            {
                "success": True,
                "message": "End user retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        obj = self.get_object(pk)
        serializer = EnquiryEndUserSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "End user updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update End user.",
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
            {"success": True, "message": "End user deleted successfully."},
            status=status.HTTP_200_OK,
        )
