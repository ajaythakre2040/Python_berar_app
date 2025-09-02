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
from lead.models.lead_logs import LeadLog  

from constants import (
        DeliveryStatus,
)

from constants import MOBILE_SKIPPED , MOBILE_VERIFIED, EMAIL_SKIPPED ,EMAIL_VERIFIED, MOBILE_PENDING ,EMAIL_PENDING

# class EnquiryVerificationCreateAPIView(APIView):

#     permission_classes = [IsAuthenticated, IsTokenValid]
#     def post(self, request, enquiry_id):
#         # print(request)
#         enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

#         channel = request.data.get("channel")
#         value = request.data.get("value")

#         if channel not in ["mobile", "email"]:
#             return Response({
#                 "success": False,
#                 "message": "Invalid verification channel."
#             }, status=400)

#         if channel == "mobile":
#             otp_code, expiry , request_id = enquiry_mobile_otp(value, user_id=request.user.id)

#         elif channel == "email":
#             otp_code, expiry, request_id = enquiry_email_otp(value, user_id=request.user.id)
#             if not otp_code:
#                 return Response({
#                     "success": False,
#                     "message": "Failed to send OTP to email."
#                 }, status=500)

#         else:
#             return Response({
#                 "success": False,
#                 "user_id": request.user.id,
#                 "message": "Invalid verification channel."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         LeadLog.objects.create(
#                     enquiry=enquiry,
#                     status="Enquiry Verification Form",
#                     created_by=request.user.id,
#                 )
        
#         return Response(
#         {
#             "status": "success",
#             "message": "OTP sent successfully.",
#             "request_id" : request_id,
#             "otp_expire": expiry,
#         },
#         status=status.HTTP_200_OK,
#         )

class EnquiryVerificationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        channel = request.data.get("channel")
        value = request.data.get("value")

        if channel not in ["mobile", "email"]:
            return Response({
                "success": False,
                "message": "Invalid verification channel."
            }, status=400)

        # 1. Send OTP
        if channel == "mobile":
            otp_code, expiry, request_id = enquiry_mobile_otp(value, user_id=request.user.id)

        elif channel == "email":
            otp_code, expiry, request_id = enquiry_email_otp(value, user_id=request.user.id)
            if not otp_code:
                return Response({
                    "success": False,
                    "message": "Failed to send OTP to email."
                }, status=500)

        # 2. Create or update EnquiryVerification row
        verification, created = EnquiryVerification.objects.get_or_create(
            enquiry=enquiry,
            defaults={"created_by": request.user.id, "created_at": timezone.now()},
        )

        if channel == "mobile":
            verification.mobile = value
            verification.mobile_status = MOBILE_PENDING
        elif channel == "email":
            verification.email = value
            verification.email_verified = EMAIL_PENDING

        verification.updated_by = request.user.id
        verification.updated_at = timezone.now()
        verification.save()

        # 3. Add LeadLog
        LeadLog.objects.create(
            enquiry=enquiry,
            status="Enquiry Verification Form (OTP Sent)",
            created_by=request.user.id,
        )

        return Response(
            {
                "status": "success",
                "message": f"OTP sent successfully to {channel}.",
                "request_id": request_id,
                "otp_expire": expiry,
            },
            status=status.HTTP_200_OK,
        )

# class otpVerificationAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsTokenValid]

#     def post(self, request, enquiry_id):
#         required_fields = ["user_id", "otp_code", "request_id", "channel", "value"]
#         missing = [field for field in required_fields if not request.data.get(field)]
#         if missing:
#             return Response(
#                 {"message": f"Missing fields: {', '.join(missing)}."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user_id = request.data["user_id"]
#         request_id = request.data["request_id"]
#         otp_code = request.data["otp_code"]
#         channel = request.data["channel"].lower()
#         value = request.data["value"]

#         enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

#         otp_record = OTP.objects.filter(user_id=user_id, request_id=request_id).order_by("-id").first()

#         if not otp_record:
#             return Response({"message": "OTP record not found."}, status=status.HTTP_404_NOT_FOUND)

#         if otp_record.status != DeliveryStatus.PENDING:
#             return Response(
#                 {"message": "OTP already used or invalid."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#         if otp_record.otp_code.strip() != otp_code.strip():
#             return Response({"message": "Incorrect OTP."}, status=status.HTTP_401_UNAUTHORIZED)


#         if timezone.now() > otp_record.expiry_at:
#             return Response({"message": "OTP has expired."}, status=status.HTTP_401_UNAUTHORIZED)

#         otp_record.status = DeliveryStatus.VERIFIED
#         otp_record.verified_at = timezone.now()
#         otp_record.save()

#         verification, created = EnquiryVerification.objects.get_or_create(
#             enquiry=enquiry,
#             defaults={"created_by": user_id, "created_at": timezone.now()}
#         )

#         if channel == "mobile":
#             verification.mobile = value
#             verification.mobile_status = MOBILE_VERIFIED
           
#             verification.save()  

#         elif channel == "email":
#             verification.email = value
#             verification.email_verified = EMAIL_VERIFIED
           
#             verification.save()  

#         else:
#             return Response({"message": "Invalid channel."}, status=status.HTTP_400_BAD_REQUEST)

#         LeadLog.objects.create(
#             enquiry=enquiry,
#             status="Enquiry Verification Success",
#             created_by=request.user.id,
#         )
#         return Response(
#             {"status": "success", "message": f"{channel.title()} OTP verified and saved."},
#             status=status.HTTP_200_OK,
#         )

class otpVerificationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

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

        # 1. Get OTP record
        otp_record = OTP.objects.filter(user_id=user_id, request_id=request_id).order_by("-id").first()
        if not otp_record:
            return Response({"message": "OTP record not found."}, status=status.HTTP_404_NOT_FOUND)

        if otp_record.status != DeliveryStatus.PENDING:
            return Response({"message": "OTP already used or invalid."}, status=status.HTTP_401_UNAUTHORIZED)

        if otp_record.otp_code.strip() != otp_code.strip():
            return Response({"message": "Incorrect OTP."}, status=status.HTTP_401_UNAUTHORIZED)

        if timezone.now() > otp_record.expiry_at:
            return Response({"message": "OTP has expired."}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Mark OTP as verified
        otp_record.status = DeliveryStatus.VERIFIED
        otp_record.verified_at = timezone.now()
        otp_record.save()

        # 3. Update existing EnquiryVerification row
        verification = EnquiryVerification.objects.filter(enquiry=enquiry).first()

        print('verification mobile', verification)


        if not verification:
            return Response({"message": "No verification record found. Please request OTP first."}, status=400)

        if channel == "mobile":
            verification.mobile = value

            print('verification value', value)

            verification.mobile_status = MOBILE_VERIFIED

            print('verification MOBILE_VERIFIED', MOBILE_VERIFIED)


        elif channel == "email":
            verification.email = value
            verification.email_verified = EMAIL_VERIFIED
        else:
            return Response({"message": "Invalid channel."}, status=status.HTTP_400_BAD_REQUEST)

        verification.updated_by = user_id
        verification.updated_at = timezone.now()
        verification.save()

        print('verification Done')

        # 4. Add LeadLog
        LeadLog.objects.create(
            enquiry=enquiry,
            status=f"Enquiry Verification Success ({channel.title()})",
            created_by=request.user.id,
        )

        return Response(
            {"status": "success", "message": f"{channel.title()} OTP verified successfully."},
            status=status.HTTP_200_OK,
        )


# class EnquiryVerificationCompleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsTokenValid]

#     def post(self, request, enquiry_id):
#         enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

#         print('request for verification', request)

#         data = request.data
#         mobile = data.get("mobile")
#         email = data.get("email")
#         aadhaar = data.get("aadhaar")

#         mobile_verified = data.get("mobile_verified", False)
#         email_verified = data.get("email_verified", False)
#         aadhaar_verified = data.get("aadhaar_verified", False)

#         user_id = request.user.id

#         verification, created = EnquiryVerification.objects.get_or_create(
#             enquiry=enquiry,
#             defaults={
#                 "created_by": user_id,
#                 "created_at": timezone.now()
#             }
#         )

#         if mobile:
#             verification.mobile = mobile
#             verification.mobile_status = MOBILE_VERIFIED if mobile_verified else MOBILE_SKIPPED
#         elif not verification.mobile:
#             verification.mobile = None
#             verification.mobile_status = MOBILE_SKIPPED

#         if email:
#             verification.email = email
#             verification.email_verified = EMAIL_VERIFIED if email_verified else EMAIL_SKIPPED
#         elif not verification.email:
#             verification.email = None
#             verification.email_verified = EMAIL_SKIPPED

#         if aadhaar:
#             verification.aadhaar = aadhaar
#             verification.aadhaar_verified = aadhaar_verified
#         elif not verification.aadhaar:
#             verification.aadhaar = None
#             verification.aadhaar_verified = False

#         verification.updated_by = user_id
#         verification.updated_at = timezone.now()
#         verification.save()


#         if (
#                 verification.mobile_status == MOBILE_VERIFIED or
#                 verification.email_verified == EMAIL_VERIFIED or
#                 verification.aadhaar_verified is True
#             ):
               

#             if int(enquiry.is_steps) < int(PercentageStatus.ENQUIRY_VERIFICATION):
#                 print("✅ Condition passed for verification step update.")
#                 enquiry.is_steps = PercentageStatus.ENQUIRY_VERIFICATION
#                 enquiry.save()
#             else:
#                 print("🔁 Enquiry already at or beyond verification step.")
#         else:
#                 print("❌ No verification method passed, skipping step update.")

#         LeadLog.objects.create(
#             enquiry=enquiry,
#             status="Enquiry Final Verification Success",
#             created_by=request.user.id,
#         )
#         return Response({
#             "status": "success",
#             "message": "Verification fields updated with verification flags.",
#             "created": created
#         }, status=status.HTTP_200_OK)

class EnquiryVerificationCompleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        data = request.data
        mobile = data.get("mobile")
        email = data.get("email")
        aadhaar = data.get("aadhaar")

        mobile_verified = data.get("mobile_verified", False)
        email_verified = data.get("email_verified", False)
        aadhaar_verified = data.get("aadhaar_verified", False)

        user_id = request.user.id

        # 1. Get existing verification row (must exist if OTP sent earlier)
        verification = EnquiryVerification.objects.filter(enquiry=enquiry).first()
        if not verification:
            return Response(
                {"message": "No verification record found. Please start verification first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Update verification fields
        if mobile:
            verification.mobile = mobile
            verification.mobile_status = MOBILE_VERIFIED if mobile_verified else MOBILE_SKIPPED
        elif not verification.mobile:
            verification.mobile_status = MOBILE_SKIPPED

        if email:
            verification.email = email
            verification.email_verified = EMAIL_VERIFIED if email_verified else EMAIL_SKIPPED
        elif not verification.email:
            verification.email_verified = EMAIL_SKIPPED

        if aadhaar:
            verification.aadhaar = aadhaar
            verification.aadhaar_verified = bool(aadhaar_verified)
        elif not verification.aadhaar:
            verification.aadhaar_verified = False

        verification.updated_by = user_id
        verification.updated_at = timezone.now()
        verification.save()

        # 3. Update enquiry step progress if any verification passed
        if (
            verification.mobile_status == MOBILE_VERIFIED
            or verification.email_verified == EMAIL_VERIFIED
            or verification.aadhaar_verified is True
        ):
            if int(enquiry.is_steps) < int(PercentageStatus.ENQUIRY_VERIFICATION):
                enquiry.is_steps = PercentageStatus.ENQUIRY_VERIFICATION
                enquiry.save()

        # 4. Add LeadLog
        LeadLog.objects.create(
            enquiry=enquiry,
            status="Enquiry Final Verification Success",
            created_by=request.user.id,
        )

        return Response({
            "status": "success",
            "message": "Verification details updated successfully.",
        }, status=status.HTTP_200_OK)
