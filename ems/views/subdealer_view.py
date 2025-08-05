from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Q

from auth_system.permissions.token_valid import IsTokenValid
from ems.models import SubDealer
from ems.serializers import SubDealerSerializer
from auth_system.utils.pagination import CustomPagination


class SubDealerListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get("search", "")
        subdealers = SubDealer.objects.filter(deleted_at__isnull=True)

        if search_query:
            subdealers = subdealers.filter(
                Q(name__icontains=search_query)
                | Q(city__icontains=search_query)
                | Q(state__icontains=search_query)
                | Q(branch_id__icontains=search_query)
                | Q(code__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(mobile_number__icontains=search_query)
            )

        subdealers = subdealers.order_by("id")
        page = request.GET.get("page")
        page_size = request.GET.get("page_size")

        if page or page_size:
            paginator = CustomPagination()
            paged_queryset = paginator.paginate_queryset(subdealers, request)
            serializer = SubDealerSerializer(paged_queryset, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "SubDealers retrieved with pagination.",
                },
            )
        else:
            serializer = SubDealerSerializer(subdealers, many=True)
            return Response(
                {
                    "success": True,
                    "message": "All subdealers retrieved successfully (no pagination).",
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

        serializer = SubDealerSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "SubDealer created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "SubDealer creation failed due to duplicate entry.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "success": False,
                "message": "Failed to create subdealer.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubDealerDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return SubDealer.objects.get(pk=pk, deleted_at__isnull=True)
        except SubDealer.DoesNotExist:
            raise NotFound(detail=f"SubDealer with id {pk} not found.")

    def get(self, request, pk):
        subdealer = self.get_object(pk)
        serializer = SubDealerSerializer(subdealer)
        return Response(
            {
                "success": True,
                "message": "SubDealer retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        subdealer = self.get_object(pk)
        serializer = SubDealerSerializer(subdealer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "SubDealer updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update subdealer.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        subdealer = self.get_object(pk)
        subdealer.soft_delete(user_id=request.user.id)
        return Response(
            {
                "success": True,
                "message": "SubDealer deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
