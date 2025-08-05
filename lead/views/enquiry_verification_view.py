from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from lead.models import Enquiry
from lead.serializers.enquiry_verifications_serializer import EnquiryVerificationSerializer
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.otp_utils import enquiry_mobile_otp , enquiry_email_otp 
from auth_system.models.otp import OTP
from django.utils import timezone
from lead.models.enquiry_verifications import EnquiryVerification
from constants import PercentageStatus

from constants import (
        DeliveryStatus,
)

from constants import MOBILE_SKIPPED , MOBILE_VERIFIED, EMAIL_SKIPPED ,EMAIL_VERIFIED


class EnquiryVerificationCreateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        print(request)
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        channel = request.data.get("channel")
        value = request.data.get("value")

        if channel not in ["mobile", "email"]:
            return Response({
                "success": False,
                "message": "Invalid verification channel."
            }, status=400)

        if channel == "mobile":
            otp_code, expiry , request_id = enquiry_mobile_otp(value, user_id=request.user.id)

        elif channel == "email":
            otp_code, expiry, request_id = enquiry_email_otp(value, user_id=request.user.id)
            if not otp_code:
                return Response({
                    "success": False,
                    "message": "Failed to send OTP to email."
                }, status=500)

        else:
            return Response({
                "success": False,
                "user_id": request.user.id,
                "message": "Invalid verification channel."
            }, status=status.HTTP_400_BAD_REQUEST)


        return Response(
        {
            "status": "success",
            "message": "OTP sent successfully.",
            "request_id" : request_id,
            "otp_expire": expiry,
        },
        status=status.HTTP_200_OK,
        )

class otpVerificationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, enquiry_id):
        required_fields = ["user_id", "otp_code", "request_id", "channel", "value"]
        missing = [field for field in required_fields if not request.data.get(field)]
        if missing:
            return Response(
                {"message": f"Missing fields: {', '.join(missing)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.data["user_id"]
        request_id = request.data["request_id"]
        otp_code = request.data["otp_code"]
        channel = request.data["channel"].lower()
        value = request.data["value"]

        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        otp_record = OTP.objects.filter(user_id=user_id, request_id=request_id).order_by("-id").first()

        if not otp_record:
            return Response({"message": "OTP record not found."}, status=status.HTTP_404_NOT_FOUND)

        if otp_record.status != DeliveryStatus.PENDING:
            return Response(
                {"message": "OTP already used or invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Compare OTP after stripping whitespace
        if otp_record.otp_code.strip() != otp_code.strip():
            return Response({"message": "Incorrect OTP."}, status=status.HTTP_401_UNAUTHORIZED)


        if timezone.now() > otp_record.expiry_at:
            return Response({"message": "OTP has expired."}, status=status.HTTP_401_UNAUTHORIZED)

        # Mark OTP as verified
        otp_record.status = DeliveryStatus.VERIFIED
        otp_record.verified_at = timezone.now()
        otp_record.save()

        # Update or create enquiry verification record
        verification, created = EnquiryVerification.objects.get_or_create(
            enquiry=enquiry,
            defaults={"created_by": user_id, "created_at": timezone.now()}
        )

        if channel == "mobile":
            verification.mobile = value
            verification.mobile_status = MOBILE_VERIFIED
            if enquiry.is_steps < PercentageStatus.ENQUIRY_VERIFICATION:
                enquiry.is_steps = PercentageStatus.ENQUIRY_VERIFICATION
                enquiry.save()  # <-- Save the update

        elif channel == "email":
            verification.email = value
            verification.email_verified = EMAIL_VERIFIED
            if enquiry.is_steps < PercentageStatus.ENQUIRY_VERIFICATION:
                enquiry.is_steps = PercentageStatus.ENQUIRY_VERIFICATION
                enquiry.save()  # <-- Save the update

        else:
            return Response({"message": "Invalid channel."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"status": "success", "message": f"{channel.title()} OTP verified and saved."},
            status=status.HTTP_200_OK,
        )

# class otpVerificationAPIView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request, enquiry_id):
#         enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

#         user_id = request.data.get("user_id")
#         request_id = request.data.get("request_id")
#         otp_code = request.data.get("otp_code")
#         channel = request.data.get("channel")  
#         value = request.data.get("value")  

#         if not user_id or not otp_code or not request_id or not channel or not value:
#             return Response(
#                 {"message": "user_id, otp_code, request_id, channel and value are required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
        
#         otp_record = OTP.objects.filter(user_id=user_id,request_id=request_id).order_by("-id").first()

#         if not otp_record:
#             return Response(
#                 {
#                     "message":"User not found"
#                 },
#                  status=status.HTTP_404_NOT_FOUND
#             )
#         if otp_record.status != DeliveryStatus.PENDING:
#             return Response(
#                 {"message": "OTP already used or invalid."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )
#         if otp_record.otp_code != otp_code:
#             return Response(
#                 {"message": "Incorrect OTP."}, status=status.HTTP_401_UNAUTHORIZED
#             )
        
#         if timezone.now() > otp_record.expiry_at:
#             return Response(
#                 {"message": "OTP has expired."}, status=status.HTTP_401_UNAUTHORIZED
#             )
        
#         otp_record.status = DeliveryStatus.VERIFIED
#         otp_record.verified_at = timezone.now()
#         otp_record.save()

#         verification, create = EnquiryVerification.objects.get_or_create(
#             enquiry=enquiry,
#             defaults={
#                 "created_by":user_id,
#                 "created_at":timezone.now()
#             }
#         )
#         if channel == "mobile":
#             verification.mobile = value
#             verification.mobile_status = MOBILE_VERIFIED
#         elif channel == "email":
#             verification.email = value
#             verification.email_verified = True

#         else:
#             return Response({
#                 "message": "Invalid channel"
#             },status=400)
        
#         verification.save()

#         return Response(
#             {
#                 "status": "success",
#                 "message": f"{channel.title()} OTP verified and saved."
#             },
#             status=status.HTTP_200_OK,
#         )

