from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django.db import IntegrityError

from ems.models import Portal
from ems.serializers.portal_serializer import PortalSerializer
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination
from django.db.models import Q

class PortalListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get('search', '')

        portals = Portal.objects.filter(deleted_at__isnull=True)

        if search_query:
            portals = portals.filter(
                Q(portal_name__icontains=search_query) |
                Q(portal_code__icontains=search_query)
            )

        portals = portals.order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(portals, request)
        serializer = PortalSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Portals retrieved successfully.",
            },
        )
    def post(self, request):
        serializer = PortalSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "message": "Portal created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Portal creation failed. Possibly a duplicate entry.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {
                "success": False,
                "message": "Failed to create portal.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PortalDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return Portal.objects.get(pk=pk, deleted_at__isnull=True)
        except Portal.DoesNotExist:
            raise NotFound(detail=f"Portal with ID {pk} not found.")

    def get(self, request, pk):
        portal = self.get_object(pk)
        serializer = PortalSerializer(portal)
        return Response(
            {
                "success": True,
                "message": "Portal retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        portal = self.get_object(pk)
        serializer = PortalSerializer(portal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Portal updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update portal.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        portal = self.get_object(pk)
        portal.deleted_at = timezone.now()
        portal.deleted_by = request.user.id
        portal.save()
        return Response(
            {
                "success": True,
                "message": "Portal deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
