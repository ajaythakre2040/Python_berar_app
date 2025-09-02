from django.db import models
from datetime import date

# -----------------------
# Admin Default Details
# -----------------------
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_MOBILE = "1234567890"
ADMIN_EMPLOYEE_CODE = "ADMIN0001"
ADMIN_FULL_NAME = "Admin"
ADMIN_DOB = date(1980, 1, 1)

ADMIN_ROLE_ID = 1
ADMIN_EMPLOYEE_ID = 1
ADMIN_BRANCH_ID = 1
ADMIN_DEPARTMENT_ID = 1
ADMIN_DESIGNATION_ID = 1
ADMIN_LEVEL = 1

ADMIN_ADDRESS = {
    "state": "Default State",
    "district": "Default District",
    "city": "Default City",
    "address": "Default Admin Address",
    "pincode": "000000",
    "longitude": None,
    "latitude": None,
    "created_by": ADMIN_EMPLOYEE_ID,
}

ADMIN_BANK_DETAILS = {
    "bank_name": "Default Bank",
    "branch_name": "Default Branch",
    "account_number": "000000000000",
    "ifsc_code": "DEFAULT0000",
    "created_by": ADMIN_EMPLOYEE_ID,
}

ADMIN_NOMINEE_DETAILS = {
    "nominee_name": "Default Nominee",
    "nominee_relation": "Self",
    "nominee_mobile": ADMIN_MOBILE,
    "nominee_email": "admin.nominee@example.com",
    "nominee_address": "Default Nominee Address",
    "created_by": ADMIN_EMPLOYEE_ID,
}

ADMIN_OFFICIAL_INFO = {
    "employment_status": 1,
    "created_by": ADMIN_EMPLOYEE_ID,
}

# -----------------------
# Login Portals
# -----------------------
LOGIN_PORTALS = {
    "EMS": 1,
    "CMS": 2,
    "LEAD": 3,
    "DEDUP": 4,
    "CODE_OF_CONDUCT": 5,
}

LOGIN_PORTAL_CHOICES = [
    (1, "EMS"),
    (2, "CMS"),
    (3, "LEAD"),
    (4, "DEDUP"),
    (5, "CODE_OF_CONDUCT"),
]

# -----------------------
# Portal Name Constants
# -----------------------
EMS = 1
CMS = 2
LEAD = 3
DEDUP = 4
CODE_OF_CONDUCT = 5

PORTAL_URL_MAP = {
    "ems": LOGIN_PORTALS["EMS"],
    "cms": LOGIN_PORTALS["CMS"],
    "lead": LOGIN_PORTALS["LEAD"],
    "dedup": LOGIN_PORTALS["DEDUP"],
    "code_of_conduct": LOGIN_PORTALS["CODE_OF_CONDUCT"],
}
# -----------------------
# Menu Name Constants
# -----------------------
DASHBOARD = 0
USER = 1
PORTAL = 2
MENU = 3
DEPARTMENT = 4
DESIGNATION = 5
BRANCH = 6
ROLE = 7
ROLEPERMISSION = 8
EMPLOYEE = 9

# -----------------------
# Permission Menu Column Constants
# -----------------------
VIEW = "view"
ADD = "add"
EDIT = "edit"
DELETE = "delete"
PRINT = "print"
EXPORT = "export"
SMSSEND = "sms_send"
APILIMIT = "api_limit"


# -----------------------
# OTP Types
# -----------------------
class OtpType(models.IntegerChoices):
    CUSTOMER_LOGIN = 1, "Customer Login"
    FD_LOGIN = 2, "FD Login"
    EMPLOYEE_LOGIN = 3, "Employee Login"
    LEAD_VERIFICATION = 4, "Lead Verification"


# -----------------------
# SMS Types
# -----------------------
class SmsType(models.IntegerChoices):
    CUSTOMER_LOGIN_OTP = 1, "Customer Login OTP"
    FD_LOGIN_OTP = 2, "FD Login OTP"
    EMPLOYEE_LOGIN_OTP = 3, "Employee Login OTP"
    LEAD_VERIFICATION_OTP = 4, "Lead Verification OTP"
    DEPOSIT_AGENT_SEND_LINK = 5, "Send Link"


# -----------------------
# SMS Constants
# -----------------------
LOGIN_OTP = 1


# -----------------------
# Delivery Status for SMS and OTP
# -----------------------
class DeliveryStatus(models.IntegerChoices):
    PENDING = 1, "Pending"
    DELIVERED = 2, "Delivered"
    FAILED = 3, "Failed"
    VERIFIED = 4, "Verified"
    EXPIRED = 5, "Expired"
    CANCELLED = 6, "Cancelled"


# -----------------------
# User Types
# -----------------------
class UserType(models.IntegerChoices):
    CUSTOMER = 1, "Customer"
    EMPLOYEE = 2, "Employee"


# -----------------------
# General Status and Errors
# -----------------------
STATUS_SUCCESS = "success"
STATUS_FAILURE = "failure"

ERROR_INVALID_CREDENTIALS = "Invalid credentials, please try again."
ERROR_ACCOUNT_LOCKED = "Account temporarily locked. Try again later."
ERROR_OTP_EXPIRED = "OTP has expired. Please request a new one."
ERROR_INVALID_OTP = "Invalid OTP. Please try again."

# -----------------------
# Security Settings
# -----------------------
MAX_LOGIN_ATTEMPTS = 3


# -----------------------
# Token Scope Constants
# -----------------------
TOKEN_SCOPE_AUTH_SYSTEM = "employee"
TOKEN_SCOPE_CUSTOMER = "customer"

EMAIL_PENDING = 0
EMAIL_VERIFIED = 1
EMAIL_SKIPPED = 2
EMAIL_STATUS_CHOICES = (
    (EMAIL_PENDING, "Pending"),
    (EMAIL_VERIFIED, "Verified"),
    (EMAIL_SKIPPED, "Skipped"),
)
MOBILE_PENDING = 0
MOBILE_VERIFIED = 1
MOBILE_SKIPPED = 2

MOBILE_STATUS_CHOICES = (
    (MOBILE_PENDING, "Pending"),
    (MOBILE_VERIFIED, "Verified"),
    (MOBILE_SKIPPED, "Skipped"),
)


# Occupation
SALARIED = 1
SELF_EMPLOYED = 2
OCCUPATION_CHOICES = ((SALARIED, "salaried"), (SELF_EMPLOYED, "Self-Employed"))


# percentage status
class PercentageStatus(models.IntegerChoices):
    ENQUIRY_BASIC = 1, "Basic"
    ENQUIRY_ADDRESS = 2, "Address"
    ENQUIRY_LOAN_DETAILS = 3, "Loan_Detail"
    ENQUIRY_VERIFICATION = 4, "Verification"
    ENQUIRY_IMAGE = 5, "Image"
    ENQUIRY_SELFIE = 6, "Selfie"


class EnquiryStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    SUBMITTED = 1, "Submitted"
    ACTIVE = 2, "Active"  # or 'Verified' — choose one
    CLOSED = 3, "Closed"
    REJECT = 4, "Reject"
    RE_OPEN = 5, "Re Open"


# --- Enquiry Types ---
TYPE_HOT = 1
TYPE_COLD = 2
ENQUIRY_TYPE_CHOICES = [
    (TYPE_HOT, "Hot"),
    (TYPE_COLD, "Cold"),
]
# --- Enquiry Loan Required On ---
TYPE_INCOME = 1
TYPE_VEHICLE = 2
TYPE_PROPERTY = 3
TYPE_LOAN_REQUIRED_ON_CHOICES = [
    (TYPE_INCOME, "Income"),
    (TYPE_VEHICLE, "Vehicle"),
    (TYPE_PROPERTY, "Property"),
]
class EmailType(models.IntegerChoices):
    ENQUIRY_VERIFICATION = 1, "Enquiry Verification OTP"


# code_of_conduct/constants.py
class QuestionTypeConstants:
    DSA = 1
    RSA = 2
    DEPOSIT_AGENT = 3

    CHOICES = [
        (DSA, 'DSA'),
        (RSA, 'RSA'),
        (DEPOSIT_AGENT, 'Deposit Agent'),
    ]

class LanguageType(models.IntegerChoices):
    HINDI = 1, "Hindi"
    ENGLISH = 2, "English"
    MARATHI = 3, "Marathi"
    GUJARATI = 4, "Gujarati"
    TELUGU = 5, "Telugu"
    KANNADA = 7, "Kannada"
    TAMIL = 8, "Tamil"
    

class EnquiryLeadStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ASSIGNED = "ASSIGNED", "Assigned"
    UPDATED = "UPDATED", "Updated"
    CLOSED = "CLOSED", "Closed"

    # percentage status



#ticket constents

class TicketPriority(models.IntegerChoices):
    LOW = 1, "Low"
    MEDIUM = 2, "Medium"
    HIGH = 3, "High"


class TicketStatus(models.IntegerChoices):
    TICKET_OPEN = 1, "OPEN"
    TICKET_CLOSED = 2, "CLOSED"
    TICKET_ACTIVE = 3, "ACTIVE"