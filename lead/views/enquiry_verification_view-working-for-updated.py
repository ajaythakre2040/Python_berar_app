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


class EnquiryVerificationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        channel = request.data.get("channel")
        value = request.data.get("value")

        if channel not in ["mobile", "email"]:
            return Response({
                "success": False,
                "message": "Invalid verification channel. Allowed: mobile or email."
            }, status=status.HTTP_400_BAD_REQUEST)

        if channel == "mobile":
            otp_code, expiry, request_id = enquiry_mobile_otp(value, user_id=request.user.id)

        elif channel == "email":
            otp_code, expiry, request_id = enquiry_email_otp(value, user_id=request.user.id)
            if not otp_code:
                return Response({
                    "success": False,
                    "message": "Failed to send OTP to email."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        LeadLog.objects.create(
            enquiry=enquiry,
            status="Enquiry Verification Form (OTP Sent)",
            created_by=request.user.id,
        )

        return Response(
            {
                "success": True,
                "message": f"OTP sent successfully to {channel}.",
                "request_id": request_id,
                "otp_expire": expiry,
            },
            status=status.HTTP_200_OK,
        )



class otpVerificationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    CHANNEL_MAP = {
        "mobile": ("mobile", "mobile_status", MOBILE_VERIFIED),
        "email": ("email", "email_verified", EMAIL_VERIFIED),
        # "aadhaar": ("aadhaar", "aadhaar_verified", AADHAAR_VERIFIED),
    }

    def post(self, request, enquiry_id):
        # ---------------- Step 1: Validate request ----------------
        required_fields = ["user_id", "otp_code", "request_id", "channel", "value"]
        missing = [f for f in required_fields if request.data.get(f) in [None, ""]]
        if missing:
            return Response(
                {"message": f"Missing fields: {', '.join(missing)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.data["user_id"]
        otp_code = request.data["otp_code"].strip()
        request_id = request.data["request_id"]
        channel = request.data["channel"].lower().strip()
        value = request.data["value"].strip()

        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)

        # ---------------- Step 2: Fetch OTP ----------------
        otp_record = (
            OTP.objects.filter(user_id=user_id, request_id=request_id)
            .order_by("-id")
            .first()
        )
        if not otp_record:
            return Response(
                {"message": "OTP record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if otp_record.status != DeliveryStatus.PENDING:
            return Response(
                {"message": "OTP already used or invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ---------------- Step 3: Validate OTP ----------------
        if timezone.now() > otp_record.expiry_at:
            return Response(
                {"message": "OTP has expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if otp_record.otp_code.strip() != otp_code:
            return Response(
                {"message": "Incorrect OTP."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ---------------- Step 4: Mark OTP verified ----------------
        otp_record.status = DeliveryStatus.VERIFIED
        otp_record.verified_at = timezone.now()
        otp_record.save()

        # ---------------- Step 5: Update EnquiryVerification ----------------
        verification = EnquiryVerification.objects.filter(enquiry=enquiry).first()
        if not verification:
            return Response(
                {"message": "No verification record found. Please request OTP first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if channel not in self.CHANNEL_MAP:
            return Response(
                {"message": "Invalid channel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        field, status_field, verified_value = self.CHANNEL_MAP[channel]
        setattr(verification, field, value)
        setattr(verification, status_field, verified_value)
        verification.updated_by = user_id
        verification.updated_at = timezone.now()
        verification.save()

        # ---------------- Step 6: Log Success ----------------
        LeadLog.objects.create(
            enquiry=enquiry,
            status=f"Enquiry Verification Success ({channel.title()})",
            created_by=request.user.id,
            remark=f"Request ID: {request_id}"
        )

        # ---------------- Step 7: Return Response ----------------
        return Response(
            {
                "status": "success",
                "message": f"{channel.title()} OTP verified successfully.",
                "verification": {
                    "mobile_status": verification.mobile_status,
                    "email_verified": verification.email_status,
                    # add more fields if needed
                },
            },
            status=status.HTTP_200_OK,
        )




class EnquiryVerificationCompleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
        user_id = request.user.id
        data = request.data

        # ---------------- Step 1: Ensure verification record exists ----------------
        verification, _ = EnquiryVerification.objects.get_or_create(
            enquiry=enquiry,
            defaults={"created_by": user_id, "created_at": timezone.now()},
        )

        # ---------------- Step 2: Process Mobile ----------------
        mobile = data.get("mobile")
        mobile_verified = bool(data.get("mobile_verified", False))
        if mobile:
            verification.mobile = mobile
            verification.mobile_status = MOBILE_VERIFIED if mobile_verified else MOBILE_SKIPPED
        elif not verification.mobile:  # if no previous mobile stored
            verification.mobile_status = MOBILE_SKIPPED

        # ---------------- Step 3: Process Email ----------------
        email = data.get("email")
        email_verified = bool(data.get("email_verified", False))
        if email:
            verification.email = email
            verification.email_verified = EMAIL_VERIFIED if email_verified else EMAIL_SKIPPED
        elif not verification.email:
            verification.email_verified = EMAIL_SKIPPED

        # ---------------- Step 4: Process Aadhaar ----------------
        aadhaar = data.get("aadhaar")
        aadhaar_verified = bool(data.get("aadhaar_verified", False))
        if aadhaar:
            verification.aadhaar = aadhaar
            verification.aadhaar_verified = aadhaar_verified
        elif not verification.aadhaar:
            verification.aadhaar_verified = False

        # ---------------- Step 5: Save verification ----------------
        verification.updated_by = user_id
        verification.updated_at = timezone.now()
        verification.save()

        # ---------------- Step 6: Update enquiry step progress ----------------
        if (
            verification.mobile_status == MOBILE_VERIFIED
            or verification.email_verified == EMAIL_VERIFIED
            or verification.aadhaar_verified is True
        ):
            if int(enquiry.is_steps) < int(PercentageStatus.ENQUIRY_VERIFICATION):
                enquiry.is_steps = PercentageStatus.ENQUIRY_VERIFICATION
                enquiry.save(update_fields=["is_steps"])

        # ---------------- Step 7: Log ----------------
        LeadLog.objects.create(
            enquiry=enquiry,
            status="Enquiry Final Verification Submitted",
            created_by=user_id,
        )

        # ---------------- Step 8: Response ----------------
        return Response(
            {
                "status": "success",
                "message": "Verification details saved (including skipped).",
                "verification": {
                    "mobile_status": verification.mobile_status,
                    "email_verified": verification.email_verified,
                    "aadhaar_verified": verification.aadhaar_verified,
                },
            },
            status=status.HTTP_200_OK,
        )
