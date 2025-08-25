from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from lead.serializers.enquiry_images_serializer import EnquiryImageSerializer
from auth_system.permissions.token_valid import IsTokenValid
from lead.models import Enquiry
from constants import PercentageStatus
from django.utils import timezone
from lead.models.lead_logs import LeadLog  
from lead.models.enquiry_images import EnquiryImages

class EnquiryImagesCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        serializer = EnquiryImageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(enquiry=enquiry, created_by=request.user.id)

                if enquiry.is_steps < PercentageStatus.ENQUIRY_IMAGE:
                    enquiry.is_steps = PercentageStatus.ENQUIRY_IMAGE
                    enquiry.updated_by = request.user.id
                    enquiry.updated_at = timezone.now()
                    enquiry.save()

                LeadLog.objects.create(
                    enquiry=enquiry,
                    status="Enquiry Image Form",
                    created_by=request.user.id,
                )

                imageData = EnquiryImages.objects.filter(enquiry=enquiry_id, deleted_at__isnull=True)

                if not imageData.exists():
                    return Response({
                        "success": False,
                        "message": "Failed to save enquiry image.",
                        "data": []
                    }, status=status.HTTP_400_BAD_REQUEST)

                serialized_images = EnquiryImageSerializer(imageData, many=True)

                return Response({
                    "success": True,
                    "message": "Enquiry image saved successfully.",
                    "data": serialized_images.data, 
                }, status=status.HTTP_201_CREATED)
            

            except IntegrityError as e:
                return Response({
                    "success": False,
                    "message": "Database integrity error while saving image.",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": False,
            "message": "Invalid data submitted for enquiry image.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class EnquiryImagesDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def delete(self, request, enquiry_id, image_id):
        image_instance = get_object_or_404(
            EnquiryImages,
            pk=image_id,
            enquiry_id=enquiry_id,
            deleted_at__isnull=True
        )

        image_instance.deleted_by = request.user.id
        image_instance.deleted_at = timezone.now()
        image_instance.save()

        remaining = EnquiryImages.objects.filter(enquiry_id=enquiry_id, deleted_at__isnull=True)
        serialized = EnquiryImageSerializer(remaining, many=True)

        return Response({
            "success": True,
            "message": "Enquiry image deleted successfully.",
            "data": serialized.data
        }, status=status.HTTP_200_OK)


class EnquiryImagesGetAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request, enquiry_id, image_id):
        image = get_object_or_404(
            EnquiryImages,
            pk=image_id,
            enquiry_id=enquiry_id,
            deleted_at__isnull=True
        )
        serializer = EnquiryImageSerializer(image)
        return Response({
            "success": True,
            "message": "Enquiry image retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class EnquiryImagesListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request, enquiry_id):
        images = EnquiryImages.objects.filter(enquiry_id=enquiry_id, deleted_at__isnull=True)
        serializer = EnquiryImageSerializer(images, many=True)
        return Response({
            "success": True,
            "message": "All enquiry images retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)