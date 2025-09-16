from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from lead.models import Enquiry
from lead.serializers.enquiry_selfie_serializer import EnquirySelfieSerializer
from auth_system.permissions.token_valid import IsTokenValid
from constants import PercentageStatus, EnquiryStatus
from django.utils import timezone
from lead.models.lead_logs import LeadLog  
from lead.models.enquiry_selfie import EnquirySelfie

    
class EnquirySelfieCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        try:
            selfie_instance = EnquirySelfie.objects.filter(
                enquiry=enquiry, deleted_at__isnull=True
            ).first()

            if selfie_instance:
                serializer = EnquirySelfieSerializer(
                    selfie_instance, data=request.data, partial=True
                )
            else:
                serializer = EnquirySelfieSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(
                    enquiry=enquiry,
                    created_by=request.user.id if not selfie_instance else selfie_instance.created_by,
                    updated_by=request.user.id,
                    updated_at=timezone.now(),
                )

                if enquiry.is_steps < PercentageStatus.ENQUIRY_SELFIE:
                    enquiry.is_steps = PercentageStatus.ENQUIRY_SELFIE

                enquiry.updated_by = request.user.id
                enquiry.updated_at = timezone.now()

                all_data_present = (
                    enquiry.enquiry_addresses.exists()
                    and enquiry.enquiry_loan_details.exists()
                    and enquiry.enquiry_images.exists()
                    and enquiry.enquiry_selfies.exists()
                )
                if all_data_present:
                    enquiry.is_status = EnquiryStatus.ACTIVE

                enquiry.save()

                LeadLog.objects.create(
                    enquiry=enquiry,
                    status="Enquiry Selfie Form",
                    created_by=request.user.id,
                )

                all_selfies = EnquirySelfieSerializer(
                    enquiry.enquiry_selfies.filter(deleted_at__isnull=True),
                    many=True,
                ).data

                return Response(
                    {
                        "success": True,
                        "message": "Selfie saved successfully.",
                        "data": all_selfies,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "success": False,
                    "message": "Invalid data submitted for selfie.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError as e:
            return Response(
                {
                    "success": False,
                    "message": "Database integrity error while saving selfie.",
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    
class EnquirySelfieReplaceAPIView(APIView):

    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id, selfie_id):

        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
        selfie_instance = get_object_or_404(EnquirySelfie, pk=selfie_id, enquiry=enquiry)

        new_selfie_file = request.FILES.get("selfie")
        if not new_selfie_file:
            return Response({
                "success": False,
                "message": "A new selfie is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        if selfie_instance.selfie:
            if selfie_instance.selfie.storage.exists(selfie_instance.selfie.name):
                selfie_instance.selfie.delete(save=False)

        selfie_instance.delete()

        data = request.data.copy()
        data["selfie"] = new_selfie_file
        serializer = EnquirySelfieSerializer(data=data)

        if serializer.is_valid():
            serializer.save(enquiry=enquiry, created_by=request.user.id)
        else:
            return Response({
                "success": False,
                "message": "Invalid selfie data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if enquiry.is_steps < PercentageStatus.ENQUIRY_SELFIE:
            enquiry.is_steps = PercentageStatus.ENQUIRY_SELFIE

        enquiry.updated_by = request.user.id
        enquiry.updated_at = timezone.now()

        all_data_present = (
            enquiry.enquiry_addresses.exists()
            and enquiry.enquiry_loan_details.exists()
            and enquiry.enquiry_images.exists()
            and enquiry.enquiry_selfies.exists()
        )
        if all_data_present:
            enquiry.is_status = EnquiryStatus.ACTIVE
        enquiry.save()

        LeadLog.objects.create(
            enquiry=enquiry,
            status="Enquiry Selfie Updated",
            created_by=request.user.id,
        )

        all_selfies = EnquirySelfieSerializer(enquiry.enquiry_selfies.all(), many=True).data

        return Response({
            "success": True,
            "message": "Selfie replaced successfully.",
            "data": all_selfies
        }, status=status.HTTP_200_OK)


class EnquirySelfieDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated, IsTokenValid]

    def delete(self, request, enquiry_id, selfie_id):
        
        image_instance = get_object_or_404(
            EnquirySelfie,
            pk=selfie_id,
            enquiry_id=enquiry_id,
            deleted_at__isnull=True
        )

        image_instance.deleted_by = request.user.id
        image_instance.deleted_at = timezone.now()
        image_instance.save()

        remaining = EnquirySelfie.objects.filter(enquiry_id=enquiry_id, deleted_at__isnull=True)
        serialized = EnquirySelfieSerializer(remaining, many=True)

        return Response({
            "success": True,
            "message": "Enquiry selfie deleted successfully.",
            "data": serialized.data
        }, status=status.HTTP_200_OK)


class EnquirySelfieGetAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request, enquiry_id, selfie_id):
        selfie_id = get_object_or_404(
            EnquirySelfie,
            pk=selfie_id,
            enquiry_id=enquiry_id,
            deleted_at__isnull=True
        )
        serializer = EnquirySelfieSerializer(selfie_id)
        return Response({
            "success": True,
            "message": "Enquiry selfie retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class EnquirySelfieListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request, enquiry_id):
        selfie_id = EnquirySelfie.objects.filter(enquiry_id=enquiry_id, deleted_at__isnull=True)
        serializer = EnquirySelfieSerializer(selfie_id, many=True)
        return Response({
            "success": True,
            "message": "All enquiry selfie retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)