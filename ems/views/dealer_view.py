from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Q

from auth_system.permissions.token_valid import IsTokenValid
from ems.models import Dealer
from ems.serializers import DealerSerializer
from auth_system.utils.pagination import CustomPagination


class DealerListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get("search", "")
        dealers = Dealer.objects.filter(deleted_at__isnull=True)

        if search_query:
            dealers = dealers.filter(
                Q(name__icontains=search_query)
                | Q(city__icontains=search_query)
                | Q(state__icontains=search_query)
                | Q(branch_id__icontains=search_query)
                | Q(code__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(mobile_number__icontains=search_query)
            )

        dealers = dealers.order_by("id")
        page = request.GET.get("page")
        page_size = request.GET.get("page_size")

        if page or page_size:
            paginator = CustomPagination()
            paged_queryset = paginator.paginate_queryset(dealers, request)
            serializer = DealerSerializer(paged_queryset, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Dealers retrieved with pagination.",
                },
            )
        else:
            serializer = DealerSerializer(dealers, many=True)
            return Response(
                {
                    "success": True,
                    "message": "All dealers retrieved successfully (no pagination).",
                    "data": serializer.data,
                }
            )

    def post(self, request):
        data = request.data.copy()

        if "image" in request.FILES:
            data["image"] = request.FILES["image"]
        if "image2" in request.FILES:
            data["image2"] = request.FILES["image2"]
        if "image3" in request.FILES:
            data["image3"] = request.FILES["image3"]

        serializer = DealerSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Dealer created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Dealer creation failed due to duplicate entry.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "success": False,
                "message": "Failed to create dealer.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DealerDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return Dealer.objects.get(pk=pk, deleted_at__isnull=True)
        except Dealer.DoesNotExist:
            raise NotFound(detail=f"Dealer with id {pk} not found.")

    def get(self, request, pk):
        dealer = self.get_object(pk)
        serializer = DealerSerializer(dealer)
        return Response(
            {
                "success": True,
                "message": "Dealer retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        dealer = self.get_object(pk)
        serializer = DealerSerializer(dealer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Dealer updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update dealer.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        dealer = self.get_object(pk)
        dealer.soft_delete(user_id=request.user.id)
        return Response(
            {
                "success": True,
                "message": "Dealer deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
