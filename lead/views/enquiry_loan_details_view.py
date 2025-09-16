from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from lead.models import Enquiry
from lead.serializers.enquiry_loan_details_serializer import EnquiryLoanDetailsSerializer
from auth_system.permissions.token_valid import IsTokenValid
from constants import PercentageStatus
from django.utils import timezone
from lead.models.lead_logs import LeadLog  
from lead.models.enquiry_loan_details import EnquiryLoanDetails


class EnquiryLoanDetailsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        enquiry_loan = EnquiryLoanDetails.objects.filter(enquiry=enquiry).first()

        if enquiry_loan:
            serializer = EnquiryLoanDetailsSerializer(enquiry_loan, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user.id, updated_at=timezone.now())

                LeadLog.objects.create(
                    enquiry=enquiry,
                    status="Enquiry Loan Details Updated",
                    created_by=request.user.id,
                )

                return Response({
                    "success": True,
                    "message": "Enquiry loan details updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                "success": False,
                "message": "Invalid data submitted for loan details update.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EnquiryLoanDetailsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                saved_instance = serializer.save(enquiry=enquiry, created_by=request.user.id)

                if enquiry.is_steps < PercentageStatus.ENQUIRY_LOAN_DETAILS:
                    enquiry.is_steps = PercentageStatus.ENQUIRY_LOAN_DETAILS
                    enquiry.updated_by = request.user.id
                    enquiry.updated_at = timezone.now()
                    enquiry.save()

                    LeadLog.objects.create(
                        enquiry=enquiry,
                        status="Enquiry Loan Details Form",
                        created_by=request.user.id,
                    )

                response_serializer = EnquiryLoanDetailsSerializer(saved_instance)

                return Response({
                    "success": True,
                    "message": "Enquiry loan details created successfully.",
                    "data": response_serializer.data
                }, status=status.HTTP_201_CREATED)

            except IntegrityError as e:
                return Response({
                    "success": False,
                    "message": "Database integrity error while saving loan details.",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": False,
            "message": "Invalid data submitted for loan details creation.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
