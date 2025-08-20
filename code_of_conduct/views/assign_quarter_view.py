from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from auth_system.utils.pagination import CustomPagination
from code_of_conduct.models.questions import Questions
from code_of_conduct.serializers.questions_serializer import QuestionsSerializer
from code_of_conduct.models.assign_quarter import AssignQuarter
from django.utils import timezone


class AssignQuarterListView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)
        type_filter = request.query_params.get("type", None)  # integer expected
        language_filter = request.query_params.get("language", None)  # ID of language
        count_only = request.query_params.get("count_only") == "true"

        filters = Q(deleted_at__isnull=True)

        if search_query:
            filters &= Q(questions__icontains=search_query)

        if type_filter is not None:
            filters &= Q(type=type_filter)

        if language_filter is not None:
            filters &= Q(language_id=language_filter)

        queryset = Questions.objects.filter(filters).order_by("id")
        total_count = queryset.count()

        if count_only:
            return Response({
                "success": True,
                "message": "Total filtered questions count retrieved.",
                "total_count": total_count
            }, status=status.HTTP_200_OK)

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page or page_size:
            page_data = paginator.paginate_queryset(queryset, request)
            serializer = QuestionsSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Questions retrieved successfully (paginated).",
                    "total_count": total_count
                }
            )
        else:
            serializer = QuestionsSerializer(queryset, many=True)
            return Response({
                "success": True,
                "message": "Questions retrieved successfully.",
                "total_count": total_count,
                "data": serializer.data,
            }, status=status.HTTP_200_OK)


class AssignQuarterCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request):
        data = request.data
        type_value = data.get("type")
        language_id = data.get("language")
        quarter_id = data.get("quarter")
        question_ids = data.get("question_ids", [])

        # Type validation
        type_map = {1: "DSA", 2: "RSA", 3: "DepositAgent"}
        valid_types = list(type_map.keys())
        if type_value not in valid_types:
            return Response({
                "success": False,
                "message": f"Invalid type: {type_value}. Allowed types are {valid_types}."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not question_ids:
            return Response({
                "success": False,
                "message": "No questions were selected."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing assignments
        existing_question_ids = list(AssignQuarter.objects.filter(
            type=type_value,
            language_id=language_id,
            quarter_id=quarter_id,
            question_id__in=question_ids,
            deleted_at__isnull=True
        ).values_list('question_id', flat=True))

        if existing_question_ids:
            # Fetch question names for the already assigned ones
            already_assigned_questions = list(Questions.objects.filter(
                id__in=existing_question_ids
            ).values_list("questions", flat=True))

            return Response({
                "success": False,
                "message": "Some questions are already assigned.",
                "already_assigned_question_ids": existing_question_ids,
                "already_assigned_questions": already_assigned_questions
            }, status=status.HTTP_400_BAD_REQUEST)

        # If all are new, proceed to create
        saved_ids = []
        for question_id in question_ids:
            assign = AssignQuarter.objects.create(
                type=type_value,
                language_id=language_id,
                quarter_id=quarter_id,
                question_id=question_id,
                created_by=request.user.id,
                created_at=timezone.now()
            )
            saved_ids.append(assign.id)

        return Response({
            "success": True,
            "message": f"{len(saved_ids)} questions successfully assigned.",
            "assigned_ids": saved_ids
        }, status=status.HTTP_201_CREATED)