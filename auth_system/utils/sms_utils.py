import requests
from django.core.mail import send_mail
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)
from decouple import config

API_SMS_KEY = config("API_SMS_KEY")


def send_seized_emp_otp(mobile_number, otp):
    url = "http://api.pinnacle.in/index.php/sms/json"
    headers = {
        "apikey": API_SMS_KEY,
        "Content-Type": "application/json",
        "Cookie": 'DO-LB="MTAuMTM5LjIyMy4xMTA6ODA="; PHPSESSID=1fo6rqls3mecq8ge6e7q6k2mmf',
    }
    payload = {
        "sender": "berarf",
        "message": [
            {
                "number": f"91{mobile_number}",
                "text": f"Dear User, Use this One Time Password: {otp} to verify your mobile number.\nIt is valid for the next 3 Minutes. Thank You Berar Finance Limited",
            }
        ],
        "messagetype": "TXT",
        "dlttempid": "1707170659123947276",
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        return response.json()
    except Exception as e:
        return {"error": "Invalid response", "content": response.text}


def send_seized_leadApp_otp(mobile_number, otp, app_signature):
    url = "http://api.pinnacle.in/index.php/sms/json"
    headers = {
        "apikey": API_SMS_KEY,
        "Content-Type": "application/json",
        "Cookie": 'DO-LB="MTAuMTM5LjIyMy4xMTA6ODA="; PHPSESSID=1fo6rqls3mecq8ge6e7q6k2mmf',
    }

    message_text = (
        f"Dear User, use this One Time Password (OTP) {otp} to verify your mobile number. "
        f"It is valid for the next 3 minutes.Thank you,Berar Finance Limited.{app_signature}"
    )

    payload = {
        "sender": "berarf",
        "message": [
            {
                "number": f"91{mobile_number}",
                "text": message_text,
            }
        ],
        "messagetype": "TXT",
        "dlttempid": "1707175759464141558",
    }

    response = requests.post(url, json=payload, headers=headers)
    try:
        return response.json()
    except Exception:
        return {"error": "Invalid response", "content": response.text}


def send_enquiry_otp_to_mobile(mobile_number, otp):
    url = "http://api.pinnacle.in/index.php/sms/json"
    headers = {
        "apikey": API_SMS_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "sender": "berarf",
        "message": [
            {
                "number": f"91{mobile_number}",
                "text": f"Dear User, Use this One Time Password: {otp} to verify your mobile number.\nIt is valid for the next 3 Minutes. Thank You Berar Finance Limited",
            }
        ],
        "messagetype": "TXT",
        "dlttempid": "1707170659123947276",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        try:
            res_json = response.json()
        except ValueError:
            print(f"Invalid JSON from SMS API: {response.text}")
            return False

        if res_json.get("status", "").lower() == "success":
            return True
        else:
            print(f"SMS API failure: {res_json}")
            return False

    except Exception as e:
        print(f"SMS API error: {e}")
        return False


def send_enquiry_otp_to_email(email, otp):
    subject = "Your OTP for Email Verification"
    message = f"""Dear User,
    Use this One Time Password: {otp} to verify your email address.
    It is valid for the next 3 minutes.
    Thank You,
    Berar Finance Limited
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    try:
        send_mail(subject, message, from_email, [email])
        return {"success": True, "message": "OTP sent to email"}
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        return {"success": False, "error": "Failed to send email", "details": str(e)}


def send_link(mobile_number, link):
    url = "http://api.pinnacle.in/index.php/sms/json"
    headers = {
        "apikey": API_SMS_KEY,
        "Content-Type": "application/json",
        "Cookie": 'DO-LB="MTAuMTM5LjIyMy4xMTA6ODA="; PHPSESSID=1fo6rqls3mecq8ge6e7q6k2mmf',
    }
    payload = {
        "sender": "berarf",
        "message": [
            {
                "number": f"91{mobile_number}",
                "text": f"Dear User, This is your link {link}. Thank You Berar Finance Limited",
            }
        ],
        "messagetype": "TXT",
        "dlttempid": "1707170659123947276",
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        return response.json()
    except Exception as e:
        return {"error": "Invalid response", "content": response.text}
