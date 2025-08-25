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

        selfie_files = request.FILES.getlist("selfie")
        if not selfie_files:
            return Response({
                "success": False,
                "message": "At least one selfie is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        for selfie_file in selfie_files:
            data = request.data.copy()
            data["selfie"] = selfie_file

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
            enquiry.is_status = EnquiryStatus.SUBMITTED
        enquiry.save()

        LeadLog.objects.create(
            enquiry=enquiry,
            status="Enquiry Selfie Form",
            created_by=request.user.id,
        )

        all_selfies = EnquirySelfieSerializer(enquiry.enquiry_selfies.all(), many=True).data

        return Response({
            "success": True,
            "message": "Selfie(s) saved successfully.",
            "data": all_selfies
        }, status=status.HTTP_201_CREATED)
    


# class EnquirySelfieReplaceAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsTokenValid]

#     def post(self, request, enquiry_id, selfie_id):

#         enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
#         selfie_instance = get_object_or_404(EnquirySelfie, pk=selfie_id, enquiry=enquiry)

#         new_selfie_file = request.FILES.get("selfie")
#         if not new_selfie_file:
#             return Response({
#                 "success": False,
#                 "message": "A new selfie is required."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         selfie_instance.delete()

#         data = request.data.copy()
#         data["selfie"] = new_selfie_file
#         serializer = EnquirySelfieSerializer(data=data)

#         if serializer.is_valid():
#             serializer.save(enquiry=enquiry, created_by=request.user.id)
#         else:
#             return Response({
#                 "success": False,
#                 "message": "Invalid selfie data.",
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Update enquiry step/status
#         if enquiry.is_steps < PercentageStatus.ENQUIRY_SELFIE:
#             enquiry.is_steps = PercentageStatus.ENQUIRY_SELFIE

#         enquiry.updated_by = request.user.id
#         enquiry.updated_at = timezone.now()

#         all_data_present = (
#             enquiry.enquiry_addresses.exists()
#             and enquiry.enquiry_loan_details.exists()
#             and enquiry.enquiry_images.exists()
#             and enquiry.enquiry_selfies.exists()
#         )
#         if all_data_present:
#             enquiry.is_status = EnquiryStatus.SUBMITTED
#         enquiry.save()

#         # Save log
#         LeadLog.objects.create(
#             enquiry=enquiry,
#             status="Enquiry Selfie Updated",
#             created_by=request.user.id,
#         )

#         all_selfies = EnquirySelfieSerializer(enquiry.enquiry_selfies.all(), many=True).data

#         return Response({
#             "success": True,
#             "message": "Selfie replaced successfully.",
#             "data": all_selfies
#         }, status=status.HTTP_200_OK)
    
    
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
            enquiry.is_status = EnquiryStatus.SUBMITTED
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
