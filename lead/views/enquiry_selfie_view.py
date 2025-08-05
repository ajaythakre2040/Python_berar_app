from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from lead.models import Enquiry
from lead.serializers.enquiry_selfie_serializer import EnquirySelfieSerializer
from auth_system.permissions.token_valid import IsTokenValid
from constants import PercentageStatus
from django.utils import timezone
from constants import EnquiryStatus


class EnquirySelfieCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        serializer = EnquirySelfieSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(enquiry=enquiry, created_by=request.user.id)

                # Update step if it's not already at or beyond ENQUIRY_SELFIE
                if enquiry.is_steps < PercentageStatus.ENQUIRY_SELFIE:
                    enquiry.is_steps = PercentageStatus.ENQUIRY_SELFIE

                # Update audit fields
                enquiry.updated_by = request.user.id
                enquiry.updated_at = timezone.now()

                # Check if all major steps are completed to mark enquiry as submitted
                all_data_present = (
                    enquiry.enquiry_addresses.exists() and
                    enquiry.enquiry_loan_details.exists() and
                    enquiry.enquiry_images.exists() and
                    enquiry.enquiry_selfies.exists()
                )

                if all_data_present:
                    enquiry.is_status = EnquiryStatus.SUBMITTED

                # Always save if any update happened
                enquiry.save()

                return Response({
                    "success": True,
                    "message": "Enquiry selfie saved and enquiry updated.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            except IntegrityError as e:
                return Response({
                    "success": False,
                    "message": "Database integrity error while saving selfie.",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": False,
            "message": "Invalid data submitted for enquiry selfie.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
