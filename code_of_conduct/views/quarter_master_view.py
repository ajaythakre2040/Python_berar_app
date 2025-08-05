from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from code_of_conduct.serializers.quarter_master_serializer import QuarterMasterSerializer
from code_of_conduct.models.quarter_master import  QuarterMaster
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework import status
from django.utils import timezone
from rest_framework.exceptions import NotFound
from auth_system.utils.pagination import CustomPagination




class QuarterMasterView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)
        
        if search_query:
            enquiries = QuarterMaster.objects.filter(
                name__icontains=search_query, deleted_at__isnull=True
            ).order_by("id")
        else:
            enquiries = QuarterMaster.objects.filter(deleted_at__isnull=True).order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page_size or page:
            page_data = paginator.paginate_queryset(enquiries, request)
            serializer = QuarterMasterSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "QuarterMaster types retrieved successfully (paginated).",
                },
            )
        else:
            serializer = QuarterMasterSerializer(enquiries, many=True)
            return Response(
                {
                    "success": True,
                    "message": "QuarterMaster types retrieved successfully.",
                    "data": serializer.data,
                }
            )
        
    def post(self, request):
      serializer = QuarterMasterSerializer(data=request.data)
      if serializer.is_valid():
        try:
            quarter_master = serializer.save(created_by=request.user.id)
            response_serializer = QuarterMasterSerializer(quarter_master)
            return Response(
                {
                    "success": True,
                    "message": "QuarterMaster type created successfully.",
                    "data": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError as e:
            return Response(
                {
                    "success": False,
                    "message": "Creation failed due to duplicate entry",
                    "error": (e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
      return Response({
        "success": False,
        "message": "Failed to create QuarterMaster type.",
        "error":serializer.errors
    },
    status=status.HTTP_400_BAD_REQUEST,
    
    )


class QuarterMasterDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return QuarterMaster.objects.get(pk=pk, deleted_at__isnull=True)
        except QuarterMaster.DoesNotExist:
            raise NotFound(detail=f"QuarterMaster type with id {pk} not found.")

    def get(self, request, pk):
        questions = self.get_object(pk)
        serializer = QuarterMasterSerializer(questions)
        return Response(
            {
                "success": True,
                "message": "QuarterMaster type retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # def patch(self, request, pk):
    #     questions = self.get_object(pk)
    #     serializer = QuarterMasterSerializer(questions, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save(updated_by=request.user.id, updated_at=timezone.now())
    #         return Response(
    #             {
    #                 "success": True,
    #                 "message": "QuarterMaster type updated successfully.",
    #                 "data": serializer.data,
    #             },
    #             status=status.HTTP_200_OK,
    #         )
    #     return Response(
    #         {
    #             "success": False,
    #             "message": "Failed to update quarter master type.",
    #             "errors": serializer.errors,
    #         },
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    def patch(self, request, pk):
        enquiry = self.get_object(pk)
        serializer = QuarterMasterSerializer(enquiry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "QuarterMaster type updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update enquiry type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

    def delete(self, request, pk):
        quarter_master  = self.get_object(pk)
        quarter_master.deleted_at = timezone.now()
        quarter_master.deleted_by = request.user.id
        quarter_master.save()

        # Return deleted brand info (optional)
        serializer = QuarterMasterSerializer(quarter_master)
        return Response(
            {
                "success": True,
                "message": "QuarterMaster type deleted successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK,
        )
