from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from auth_system.models.last_three_passwords import LastThreePasswords
from auth_system.models.login_fail_attempts import LoginFailAttempts
from auth_system.models.password_attempt import PasswordAttemptLogs
from auth_system.models.user import TblUser
from auth_system.serializers import TblUserSerializer
from auth_system.utils.common import (
    generate_otp,
    otp_expiry_time,
    validate_password,
    generate_request_id,
)
from auth_system.models.blacklist import BlackListedToken
from auth_system.models.login_session import LoginSession
from auth_system.models.otp import OTP
from auth_system.models.sms_log import SmsLog
from auth_system.permissions.token_valid import (
    IsTokenValid,
)
from auth_system.utils.pagination import CustomPagination
from auth_system.utils.session_utils import create_login_session
from auth_system.utils.sms_utils import send_seized_emp_otp
from auth_system.utils.token_utils import generate_token

from constants import (
    OtpType,
    SmsType,
    DeliveryStatus,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_PORTALS,
    LEAD,
)
import re
from auth_system.utils.otp_utils import send_login_otp, send_Applogin_otp
from auth_system.utils.common import get_client_ip_and_agent


class UserListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = TblUser.objects.filter(is_deleted=False).order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = TblUserSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={"success": True, "message": "Users retrieved successfully."},
        )

    def post(self, request):
        serializer = TblUserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "status_code": status.HTTP_201_CREATED,
                    "message": "User registered successfully.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Registration failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get("username")
        password = data.get("password")
        login_portal = data.get("portal_id", 1)

        ip_address, agent_browser = get_client_ip_and_agent(request)

        if not all([username, password]):
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "username and password are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self._get_user(username)
        if not user:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Incorrect username.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.login_attempt >= MAX_LOGIN_ATTEMPTS:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Account locked. Try later.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not check_password(password, user.password):
            self._log_failed_attempt(user, username, ip_address, agent_browser)
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Incorrect password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.login_attempt = 0
        user.is_login = True
        user.save()
        LoginFailAttempts.objects.filter(username=username).delete()

        if not user.two_step:
            tokens = generate_token(user, portal_id=login_portal)
            access_token = tokens["access"]
            refresh_token = tokens["refresh"]

            create_login_session(
                user.id,
                login_portal,
                access_token,
                ip_address,
                agent_browser,
                request.headers,
            )

            return Response(
                {
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Login successful.",
                    "empoyee_id": user.employee_id,
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                },
                status=status.HTTP_200_OK,
            )

        otp_code, expiry, request_id = send_login_otp(user)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "OTP sent successfully.",
                "user": user.id,
                "accessToken": False,
                "request_id": request_id,
                "two_step": True,
                "otp_expire": expiry,
            },
            status=status.HTTP_200_OK,
        )

    def _get_user(self, username):
        if username.isdigit() and len(username) == 10:
            return TblUser.objects.filter(mobile_number=username).first()
        elif "@" in username:
            return TblUser.objects.filter(email=username).first()
        return None

    def _log_failed_attempt(self, user, username, ip, agent_browser):
        user.login_attempt += 1
        user.save()
        LoginFailAttempts.objects.create(
            username=username,
            ip=ip,
            agent_browser=agent_browser,
            user_details={
                "id": user.id,
                "username": username,
                "employee_code": user.employee_code,
                "mobile_number": user.mobile_number,
                "email": user.email,
            },
            created_at=timezone.now(),
        )


class TwoFactorVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp_code")
        login_portal = request.data.get("portal_id", 1)

        ip_address, agent_browser = get_client_ip_and_agent(request)
        request_id = request.data.get("request_id")

        if not user_id or not otp_code or not request_id:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "user_id, otp_code and request_id are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if login_portal not in LOGIN_PORTALS.values():
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid portal_id provided.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = TblUser.objects.get(id=user_id)
        except TblUser.DoesNotExist:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        otp_record = (
            OTP.objects.filter(user_id=user_id, request_id=request_id)
            .order_by("-id")
            .first()
        )

        if not otp_record:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "OTP not found for this request ID.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if otp_record.status != DeliveryStatus.PENDING:
            return Response(
                {
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "OTP already used or invalid.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if otp_record.otp_code != otp_code:
            return Response(
                {
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Incorrect OTP.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if timezone.now() > otp_record.expiry_at:
            return Response(
                {
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "OTP has expired.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        otp_record.status = DeliveryStatus.VERIFIED
        otp_record.verified_at = timezone.now()
        otp_record.save()

        user.is_login = True
        user.login_attempt = 0
        user.save()

        tokens = generate_token(user, portal_id=login_portal)
        create_login_session(
            user.id,
            login_portal,
            tokens["access"],
            ip_address,
            agent_browser,
            request.headers,
        )

        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "success": True,
                "message": "OTP verified successfully.",
                "accessToken": tokens["access"],
                "refreshToken": tokens["refresh"],
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User ID is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = TblUser.objects.get(id=user_id)
        except TblUser.DoesNotExist:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if not user.mobile_number:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Mobile number not associated with user.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_code, expiry, request_id = send_login_otp(user)
        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "status": "success",
                "message": "OTP resent successfully.",
                "otp_expire": expiry,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        auth_header = request.headers.get("Authorization")

        if (
            not refresh_token
            or not auth_header
            or not auth_header.startswith("Bearer ")
        ):
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Both refresh and access tokens are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = auth_header.split(" ")[1]

        ip_address = request.META.get("REMOTE_ADDR")
        agent_browser = request.headers.get("User-Agent")

        session = (
            LoginSession.objects.filter(
                user=request.user,
                is_active=True,
                logout_at__isnull=True,
                ip_address=ip_address,
                agent_browser=agent_browser,
            )
            .order_by("-login_at")
            .first()
        )

        if not session:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "No active login session found for this device and IP.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if session.token != access_token:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access token does not match the active session.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            session.is_active = False
            session.logout_at = timezone.now()
            session.save()

            user = request.user
            user.is_login = False
            user.save(update_fields=["is_login"])

            RefreshToken(refresh_token).blacklist()

            BlackListedToken.objects.bulk_create(
                [
                    BlackListedToken(token=access_token, user=user),
                    BlackListedToken(token=refresh_token, user=user),
                ]
            )

            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Logout successful.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "An error occurred during logout.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LeadLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        mobile_number = data.get("mobile_number")
        portal_id = data.get("portal_id")
        app_signature = data.get("app_signature")
        if not app_signature:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "App signature is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not mobile_number or not re.match(r"^\+?[0-9]{10,15}$", mobile_number):
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid mobile number format.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not mobile_number:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "mobile number is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if portal_id not in LOGIN_PORTALS.values():
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid portal_id provided.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self._get_user(mobile_number)

        if not user:
            return Response(
                {
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Incorrect mobile number.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        otp_code, expiry, request_id = send_Applogin_otp(user, app_signature)

        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "status": "success",
                "message": "OTP sent successfully.",
                "user": user.id,
                "portal_id": portal_id,
                "request_id": request_id,
                "otp_expire": expiry,
            },
            status=status.HTTP_200_OK,
        )

    def _get_user(self, mobile_number):
        if mobile_number.isdigit() and len(mobile_number) == 10:
            return TblUser.objects.filter(mobile_number=mobile_number).first()
        return None


class LeadTwoFactorVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        user_id = data.get("user_id")
        request_id = data.get("request_id")
        otp_code = data.get("otp_code")
        login_portal = data.get("portal_id")

        ip_address, agent_browser = get_client_ip_and_agent(request)

        if not user_id or not otp_code or not request_id or not login_portal:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "user_id, request_id, otp_code, and portal_id are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if login_portal not in LOGIN_PORTALS.values():
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid portal_id provided.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = TblUser.objects.get(id=user_id)
        except TblUser.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        otp_record = (
            OTP.objects.filter(user_id=user_id, request_id=request_id)
            .order_by("-id")
            .first()
        )

        if not otp_record:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "OTP not found for this request ID.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if otp_record.status != DeliveryStatus.PENDING:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "OTP already used or invalid.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if otp_record.otp_code != otp_code:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Incorrect OTP.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if timezone.now() > otp_record.expiry_at:
            return Response(
                {
                    "status": "error",
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "OTP has expired.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        otp_record.status = DeliveryStatus.VERIFIED
        otp_record.verified_at = timezone.now()
        otp_record.save()

        user.is_login = True
        user.login_attempt = 0
        user.save()

        tokens = generate_token(user, portal_id=login_portal)

        create_login_session(
            user_id=user.id,
            login_portal=login_portal,
            token=tokens["access"],
            ip_address=ip_address,
            agent_browser=agent_browser,
            headers=request.headers,
        )
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "OTP verified successfully.",
                "accessToken": tokens["access"],
                "refreshToken": tokens["refresh"],
            },
            status=status.HTTP_200_OK,
        )
