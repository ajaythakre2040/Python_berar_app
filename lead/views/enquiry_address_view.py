# lead/views/enquiry_address.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from lead.serializers.enquiry_address_serializer import EnquiryAddressSerializer
from auth_system.permissions.token_valid import IsTokenValid
from lead.models import Enquiry
from constants import PercentageStatus
from django.utils import timezone
from lead.models.lead_logs import LeadLog  


class EnquiryAddressCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        serializer = EnquiryAddressSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(enquiry=enquiry, created_by=request.user.id)

                if enquiry.is_steps < PercentageStatus.ENQUIRY_ADDRESS:
                    enquiry.is_steps = PercentageStatus.ENQUIRY_ADDRESS
                    enquiry.updated_by = request.user.id
                    enquiry.updated_at = timezone.now()
                    enquiry.save()

                    LeadLog.objects.create(
                        enquiry=enquiry,
                        status="Enquiry Address Form",
                        created_by=request.user.id,
                    )
            
                return Response(
                    {
                        "success": True,
                        "message": "Enquiry address created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Database integrity error while saving address.",
                        "error": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {
                "success": False,
                "message": "Invalid data submitted for enquiry address.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
