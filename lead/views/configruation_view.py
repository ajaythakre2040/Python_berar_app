from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from auth_system.permissions.token_valid import IsTokenValid
from lead.models.configuration import Configuration
from lead.serializers.configuration_serializer import ConfigurationSerializer


class ConfigurationListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        configs = Configuration.objects.filter(deleted_at__isnull=True).order_by("-id")
        serializer = ConfigurationSerializer(configs, many=True)
        return Response({
            "success": True,
            "message": "Configurations retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                config = serializer.save(created_by=request.user.id)
                return Response({
                    "success": True,
                    "message": "Configuration created successfully.",
                    # "data": ConfigurationSerializer(config).data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({
                    "success": False,
                    "message": "Integrity error occurred.",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "success": False,
                "message": "Invalid data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class ConfigurationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        return get_object_or_404(Configuration, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        config = self.get_object(pk)
        serializer = ConfigurationSerializer(config)
        return Response({
            "success": True,
            "message": "Configuration retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        config = self.get_object(pk)
        serializer = ConfigurationSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            config = serializer.save(updated_by=request.user.id)
            return Response({
                "success": True,
                "message": "Configuration updated successfully.",
                "data": ConfigurationSerializer(config).data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
