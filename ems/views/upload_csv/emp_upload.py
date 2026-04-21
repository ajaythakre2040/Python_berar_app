import pandas as pd
import io, os
from datetime import datetime
from decimal import Decimal
from tqdm import tqdm

from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Models
from ems.models.emp_basic_profile import TblEmpBasicProfile
from ems.models.emp_official_information import TblEmpOfficialInformation
from ems.models.emp_address_details import TblEmpAddressDetails
from ems.models.emp_bank_details import TblEmpBankDetails
from ems.models.emp_nominee_details import TblEmpNomineeDetails
from auth_system.models import TblUser
from ...models.branch import TblBranch
from ...models.department import TblDepartment
from ...models.designation import TblDesignation
from ...models.role import Role


class UploadCSVView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        log_directory = os.path.join(settings.MEDIA_ROOT, "error_logs")
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        try:
            print(f"--- Process Started: {timestamp} ---")
            file_data = file.read().decode("utf-8", errors="replace")
            df = pd.read_csv(io.StringIO(file_data))
            df = df.where(pd.notnull(df), None)
            df.columns = df.columns.str.strip()
            total_rows = len(df)

            # 1. Master Data Caching (For Speed)
            branches = {
                str(b.branch_name).lower().strip(): b.id
                for b in TblBranch.objects.all()
            }
            depts = {
                str(d.department_name).lower().strip(): d.id
                for d in TblDepartment.objects.all()
            }
            desigs = {
                str(ds.designation_name).lower().strip(): ds.id
                for ds in TblDesignation.objects.all()
            }
            roles = {str(r.role_name).lower().strip(): r.id for r in Role.objects.all()}
            name_to_id_map = self.get_employee_name_map()

            # 2. Database Unique Constraint Checks (Email/Mobile/Code)
            db_codes = set(
                TblEmpBasicProfile.objects.values_list("employee_code", flat=True)
            )
            db_mobiles = set(
                str(m).split(".")[0]
                for m in TblEmpBasicProfile.objects.exclude(
                    mobile_number=None
                ).values_list("mobile_number", flat=True)
            )

            # Fix: Checking email in both tables to prevent "Duplicate Key" crash
            emp_emails = set(
                e.lower()
                for e in TblEmpBasicProfile.objects.exclude(email=None).values_list(
                    "email", flat=True
                )
            )
            user_emails = set(
                e.lower()
                for e in TblUser.objects.exclude(email=None).values_list(
                    "email", flat=True
                )
            )
            db_emails = emp_emails.union(user_emails)

            valid_data_list = []
            failed_records = []
            csv_codes, csv_mobiles, csv_emails = set(), set(), set()
            creator_id = (
                request.user.id if request.user and request.user.is_authenticated else 1
            )

            # 3. Validation Phase
            for i, row in tqdm(df.iterrows(), total=total_rows, desc="Validating"):
                row_idx = i + 2
                emp_name = self.sanitize_str(row.get("name"))
                emp_code = self.sanitize_str(row.get("employee_code"))
                mobile = self.sanitize_str(row.get("mobile_number"), is_mobile=True)
                email = self.sanitize_str(row.get("email"), lower=True)

                reasons = []

                # Check Unique constraints
                if not emp_code:
                    reasons.append("Emp Code Missing")
                elif emp_code in db_codes:
                    reasons.append(f"Code '{emp_code}' exists in DB")
                elif emp_code in csv_codes:
                    reasons.append(f"Code '{emp_code}' duplicate in CSV")

                if not mobile:
                    reasons.append("Mobile Missing")
                elif mobile in db_mobiles:
                    reasons.append(f"Mobile '{mobile}' exists in DB")
                elif mobile in csv_mobiles:
                    reasons.append(f"Mobile '{mobile}' duplicate in CSV")

                if email:
                    if email in db_emails:
                        reasons.append(f"Email '{email}' exists in DB")
                    elif email in csv_emails:
                        reasons.append(f"Email '{email}' duplicate in CSV")

                # Check Master Data
                b_name = str(row.get("branch", "")).strip()
                b_id = branches.get(b_name.lower())
                if not b_id:
                    reasons.append(f"Branch '{b_name}' not found")

                if reasons:
                    row_dict = row.to_dict()
                    row_dict["error_reason"] = " | ".join(reasons)
                    row_dict["row_number"] = row_idx
                    failed_records.append(row_dict)
                    continue

                # Store valid metadata
                csv_codes.add(emp_code)
                csv_mobiles.add(mobile)
                if email:
                    csv_emails.add(email)

                valid_data_list.append(
                    {
                        "row": row,
                        "emp_code": emp_code,
                        "mobile": mobile,
                        "emp_name": emp_name,
                        "email": email,
                        "branch_id": b_id,
                        "dept_id": depts.get(
                            str(row.get("department", "")).lower().strip()
                        ),
                        "desig_id": desigs.get(
                            str(row.get("designation", "")).lower().strip()
                        ),
                        "role_id": roles.get(str(row.get("role", "")).lower().strip()),
                    }
                )

            # 4. Atomic Insertion Phase (The most critical part)
            if valid_data_list:
                with transaction.atomic():
                    # A. Create Basic Profiles first (Foreign Key parent)
                    profiles_to_create = [
                        TblEmpBasicProfile(
                            employee_code=m["emp_code"],
                            name=m["emp_name"] or "Unknown",
                            email=m["email"],
                            mobile_number=m["mobile"],
                            dob=self.parse_date(m["row"].get("dob")) or "1900-01-01",
                            gender=str(m["row"].get("gender", "Male")),
                            created_by=creator_id,
                        )
                        for m in valid_data_list
                    ]
                    created_profiles = TblEmpBasicProfile.objects.bulk_create(
                        profiles_to_create
                    )

                    # B. Prepare all other tables
                    users, addresses, banks, nominees, officials = [], [], [], [], []

                    for idx, p in enumerate(created_profiles):
                        meta = valid_data_list[idx]
                        r = meta["row"]

                        # Password Hashing (Using MD5 for faster bulk import)
                        name_p = p.name[:4].capitalize() if p.name else "User"
                        mobile_p = p.mobile_number[-4:] if p.mobile_number else "0000"
                        hashed_pwd = make_password(f"{name_p}@{mobile_p}", hasher="md5")

                        # 1. User Table
                        users.append(
                            TblUser(
                                full_name=p.name,
                                mobile_number=p.mobile_number,
                                email=p.email or f"u_{p.employee_code}@company.com",
                                password=hashed_pwd,
                                employee_id=p.id,
                                employee_code=p.employee_code,
                                branch_id_id=meta["branch_id"],
                                department_id_id=meta["dept_id"],
                                designation_id_id=meta["desig_id"],
                                role_id_id=meta["role_id"],
                                is_active=True,
                                created_by=creator_id,
                            )
                        )

                        # 2. Address Details
                        addresses.append(
                            TblEmpAddressDetails(
                                employee_id=p,
                                address=r.get("address"),
                                city=r.get("city"),
                                state=r.get("state"),
                                pincode=r.get("pincode"),
                                created_by=creator_id,
                                longitude=self.parse_decimal(r.get("longitude")),
                                latitude=self.parse_decimal(r.get("latitude")),
                            )
                        )

                        # 3. Bank Details
                        banks.append(
                            TblEmpBankDetails(
                                employee_id=p,
                                bank_name=r.get("bank_name"),
                                branch_name=r.get("branch_name"),
                                account_number=r.get("account_number"),
                                ifsc_code=r.get("ifsc_code"),
                                created_by=creator_id,
                            )
                        )

                        # 4. Nominee Details
                        nominees.append(
                            TblEmpNomineeDetails(
                                employee_id=p,
                                nominee_name=r.get("nominee_name"),
                                nominee_relation=r.get("nominee_relation"),
                                nominee_mobile=self.sanitize_str(
                                    r.get("nominee_mobile"), is_mobile=True
                                ),
                                nominee_email=self.sanitize_str(
                                    r.get("nominee_email"), lower=True
                                ),
                                created_by=creator_id,
                            )
                        )

                        # 5. Official Info
                        officials.append(
                            TblEmpOfficialInformation(
                                employee_id=p,
                                employment_status=1,
                                reporting_to_id=name_to_id_map.get(
                                    str(r.get("reporting_to", "")).lower().strip()
                                ),
                                remarks=r.get("remarks"),
                                created_by=creator_id,
                            )
                        )

                    # C. Bulk Insert everything into DB
                    TblUser.objects.bulk_create(users, batch_size=500)
                    TblEmpAddressDetails.objects.bulk_create(addresses, batch_size=500)
                    TblEmpBankDetails.objects.bulk_create(banks, batch_size=500)
                    TblEmpNomineeDetails.objects.bulk_create(nominees, batch_size=500)
                    TblEmpOfficialInformation.objects.bulk_create(
                        officials, batch_size=500
                    )

            print(f"--- Finished: {len(valid_data_list)} records created ---")
            return Response(
                {
                    "status": "Success",
                    "inserted": len(valid_data_list),
                    "failed": len(failed_records),
                    "error_report": self.get_error_url(
                        failed_records, log_directory, timestamp, request
                    ),
                }
            )

        except Exception as e:
            return Response(
                {"error": "Bulk Create Failed", "details": str(e)}, status=500
            )

    # --- Helper Methods ---
    def sanitize_str(self, val, lower=False, is_mobile=False):
        if val is None or pd.isna(val):
            return None
        s = str(val).strip()
        if s.lower() in ["nan", "none", "", "null"]:
            return None
        if is_mobile:
            s = s.split(".")[0]
        return s.lower() if lower else s

    def parse_decimal(self, value):
        if (
            value is None
            or pd.isna(value)
            or str(value).strip().lower() in ["nan", "none", ""]
        ):
            return None
        try:
            return Decimal(str(value).strip())
        except:
            return None

    def get_employee_name_map(self):
        return {
            str(name).lower().strip(): emp_id
            for emp_id, name in TblEmpBasicProfile.objects.values_list("id", "name")
        }

    def parse_date(self, d):
        if not d or pd.isna(d):
            return None
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(d).strip(), fmt).date()
            except:
                continue
        return None

    def get_error_url(self, records, path, ts, req):
        if not records:
            return None
        file_name = f"failed_ems_{ts}.csv"
        pd.DataFrame(records).to_csv(os.path.join(path, file_name), index=False)
        return req.build_absolute_uri(f"{settings.MEDIA_URL}error_logs/{file_name}")
