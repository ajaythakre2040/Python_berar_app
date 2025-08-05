from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from code_of_conduct.serializers.questions_serializer import QuestionsSerializer
from code_of_conduct.models.questions import Questions
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework import status
from django.utils import timezone
from rest_framework.exceptions import NotFound
from auth_system.utils.pagination import CustomPagination



class QuestionsListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)

        if search_query:
            enquiries = Questions.objects.filter(
                name__icontains=search_query, deleted_at__isnull=True
            ).order_by("id")
        else:
            enquiries = Questions.objects.filter(deleted_at__isnull=True).order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page_size or page:
            page_data = paginator.paginate_queryset(enquiries, request)
            serializer = QuestionsSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Questions types retrieved successfully (paginated).",
                },
            )
        else:
            serializer = QuestionsSerializer(enquiries, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Questions types retrieved successfully.",
                    "data": serializer.data,
                }
            )
        
    def post(self, request):
      serializer = QuestionsSerializer(data=request.data)
      if serializer.is_valid():
        try:
            questions = serializer.save(created_by=request.user.id)
            response_serializer = QuestionsSerializer(questions)
            return Response(
                {
                    "success": True,
                    "message": "Questions type created successfully.",
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
        "message": "Failed to create Questions type.",
        "error":serializer.errors
    },
    status=status.HTTP_400_BAD_REQUEST,
    
    )
    
    
class QuestionsDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return Questions.objects.get(pk=pk, deleted_at__isnull=True)
        except Questions.DoesNotExist:
            raise NotFound(detail=f"Questions type with id {pk} not found.")

    def get(self, request, pk):
        questions = self.get_object(pk)
        serializer = QuestionsSerializer(questions)
        return Response(
            {
                "success": True,
                "message": "Questions type retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        questions = self.get_object(pk)
        serializer = QuestionsSerializer(questions, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Questions type updated successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update question type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        questions = self.get_object(pk)
        questions.deleted_at = timezone.now()
        questions.deleted_by = request.user.id
        questions.save()

        # Return deleted brand info (optional)
        serializer = QuestionsSerializer(questions)
        return Response(
            {
                "success": True,
                "message": "Questions type deleted successfully.",
                # "data": serializer.data
            },
            status=status.HTTP_200_OK,
        )
