from django.utils import timezone
from auth_system.models.email_logs import EmailLogs
from auth_system.models.otp import OTP
from auth_system.models.sms_log import SmsLog
from auth_system.utils.common import generate_otp, otp_expiry_time, generate_request_id
from auth_system.utils.sms_utils import send_enquiry_otp_to_email,send_link
from constants import EmailType, OtpType, SmsType, DeliveryStatus


def send_login_otp(user):
    otp_code = generate_otp()
    expiry = otp_expiry_time()
    request_id = generate_request_id()
    mobile = user.mobile_number
    # sms_status = (
    #     DeliveryStatus.DELIVERED
    #     if send_seized_emp_otp(mobile, otp_code)
    #     else DeliveryStatus.FAILED
    # )
    sms_status = DeliveryStatus.DELIVERED
    OTP.objects.create(
        user_id=user.id,
        otp_type=OtpType.EMPLOYEE_LOGIN,
        otp_code=otp_code,
        expiry_at=expiry,
        status=DeliveryStatus.PENDING,
        request_id=request_id,
    )
    SmsLog.objects.create(
        user_id=user.id,
        mobile_number=mobile,
        message=f"Your OTP is {otp_code}. It is valid for 5 minutes.",
        sms_type=SmsType.EMPLOYEE_LOGIN_OTP,
        request_id=request_id,
        status=sms_status,
        sent_at=timezone.now(),
    )
    return otp_code, expiry, request_id


def enquiry_mobile_otp(mobile, user_id=None):
    otp_code = generate_otp()
    expiry = otp_expiry_time()
    request_id = generate_request_id()
    # sms_status = (
    #     DeliveryStatus.DELIVERED
    #     if send_enquiry_otp_to_mobile(mobile, otp_code)
    #     else DeliveryStatus.FAILED
    # )
    sms_status = DeliveryStatus.DELIVERED
    OTP.objects.create(
        user_id=user_id,
        otp_type=OtpType.LEAD_VERIFICATION,
        otp_code=otp_code,
        expiry_at=expiry,
        status=DeliveryStatus.PENDING,
        request_id=request_id,
    )
    SmsLog.objects.create(
        user_id=user_id,
        mobile_number=mobile,
        message=f"Your OTP is {otp_code}. It is valid for 5 minutes.",
        sms_type=SmsType.LEAD_VERIFICATION_OTP,
        request_id=request_id,
        status=sms_status,
        sent_at=timezone.now(),
    )
    return otp_code, expiry, request_id


def enquiry_email_otp(email, user_id=None):
    otp_code = generate_otp()
    expiry = otp_expiry_time()
    request_id = generate_request_id()
    result = send_enquiry_otp_to_email(email, otp_code)
    if not result.get("success"):
        return None, None
    OTP.objects.create(
        user_id=user_id,
        otp_type=OtpType.LEAD_VERIFICATION,
        otp_code=otp_code,
        expiry_at=expiry,
        status=DeliveryStatus.PENDING,
        request_id=request_id,
    )
    return otp_code, expiry, request_id


def enquiry_email_otp(email, user_id=None):
    otp_code = generate_otp()
    expiry = otp_expiry_time()
    request_id = generate_request_id()
    result = send_enquiry_otp_to_email(email, otp_code)
    if not result.get("success"):
        return None, None, None
    OTP.objects.create(
        user_id=user_id,
        otp_type=OtpType.LEAD_VERIFICATION,
        otp_code=otp_code,
        expiry_at=expiry,
        status=DeliveryStatus.PENDING,
        request_id=request_id,
    )
    EmailLogs.objects.create(
        user_id=user_id,
        email=email,
        message=f"Your OTP is {otp_code}. It is valid for 3 minutes.",
        email_type=EmailType.ENQUIRY_VERIFICATION,
        request_id=request_id,
        status=DeliveryStatus.DELIVERED,
        sent_at=timezone.now(),
    )
    return otp_code, expiry, request_id


def send_link_to_mobile(request, mobile, link):
    # api_response = send_link(mobile, link)

    # sms_status = (
    #     DeliveryStatus.DELIVERED
    #     if api_response and not api_response.get("error")
    #     else DeliveryStatus.FAILED
    # )

    api_response = {
        "code": 200,
        "status": "success",
        "data": [
            {
                "mobile": f"91{mobile}",
                "uniqueid": "dummy_unique_id_123456"
            }
        ]
    }

    sms_status = DeliveryStatus.DELIVERED  # Always mark as delivered for dev

    SmsLog.objects.create(
        user_id=request.user.id,
        mobile_number=mobile,
        message=f"Your Link {link}.",
        sms_type=SmsType.DEPOSIT_AGENT_SEND_LINK,
        status=sms_status,
        sent_at=timezone.now(),
    )

    return api_response  
