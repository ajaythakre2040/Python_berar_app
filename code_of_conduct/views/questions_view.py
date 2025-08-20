from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from code_of_conduct.serializers.questions_serializer import QuestionsSerializer
from code_of_conduct.models.questions import Questions
from constants import QuestionTypeConstants  # constant import
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
            questions = Questions.objects.filter(
                questions__icontains=search_query, deleted_at__isnull=True
            ).order_by("id")
        else:
            questions = Questions.objects.filter(deleted_at__isnull=True).order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page_size or page:
            page_data = paginator.paginate_queryset(questions, request)
            serializer = QuestionsSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Questions retrieved successfully (paginated).",
                },
            )
        else:
            serializer = QuestionsSerializer(questions, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Questions retrieved successfully.",
                    "data": serializer.data,
                }
            )
        
    def post(self, request):

        # print('user id chahhiye idhar',request.user.id) 1
        serializer = QuestionsSerializer(data=request.data)
        if serializer.is_valid():
            # Duplicate check manually
            question_text = serializer.validated_data.get('questions')
            language = serializer.validated_data.get('language')
            q_type = serializer.validated_data.get('type')

            # check if a question with same text, language, and type already exists
            exists = Questions.objects.filter(
                questions=question_text,
                language=language,
                type=q_type
            ).exists()

            if exists:
                return Response({
                    "success": False,
                    "message": "Question already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Question created successfully."
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Creation failed due to integrity error.",
                        "error": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response({
            "success": False,
            "message": "Validation failed.",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
   

class QuestionsDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return Questions.objects.get(pk=pk, deleted_at__isnull=True)
        except Questions.DoesNotExist:
            raise NotFound(detail=f"Question with ID {pk} not found.")

    def get(self, request, pk):
        question = self.get_object(pk)
        serializer = QuestionsSerializer(question)
        return Response(
            {
                "success": True,
                "message": "Question retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        question = self.get_object(pk)
        serializer = QuestionsSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Question updated successfully.",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Update failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        question = self.get_object(pk)
        question.deleted_at = timezone.now()
        question.deleted_by = request.user.id
        question.save()

        return Response(
            {
                "success": True,
                "message": "Question deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class QuestionsTypeConstantsView(APIView):
    def get(self, request):
        data = [
            {"id": QuestionTypeConstants.DSA, "name": "DSA"},
            {"id": QuestionTypeConstants.RSA, "name": "RSA"},
            {"id": QuestionTypeConstants.DEPOSIT_AGENT, "name": "Deposit Agent"},
        ]
        return Response({
            "success": True,
            "data": data
        }, status=status.HTTP_200_OK)
