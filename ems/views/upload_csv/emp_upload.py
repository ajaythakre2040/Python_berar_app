import pandas as pd
from datetime import datetime
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ems.models.emp_basic_profile import TblEmpBasicProfile
from ems.models.emp_address_details import TblEmpAddressDetails
from ems.models.emp_bank_details import TblEmpBankDetails
from ems.models.emp_nominee_details import TblEmpNomineeDetails
from ems.models.emp_official_information import TblEmpOfficialInformation
from auth_system.models import TblUser

from ...models.branch import TblBranch
from ...models.department import TblDepartment
from ...models.designation import TblDesignation
from ...models.role import Role


def parse_custom_date(date_str):
    if pd.isna(date_str) or not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_int(value):
    try:
        if pd.isna(value) or value == "":
            return None
        return int(value)
    except (ValueError, TypeError):
        return None


def get_instance_or_none(model, pk):
    if not pk:
        return None
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None


def parse_decimal(value):
    try:
        if pd.isna(value) or value == "" or str(value).lower() == "nan":
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def clean_string(value):
    if pd.isna(value) or str(value).strip().lower() in ["nan", "none", "null", ""]:
        return None
    return str(value).strip()


class UploadCSVView(APIView):
    def post(self, request):
        print("Received upload request")

        file = request.FILES.get("file")
        if not file:
            print("No file provided")
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not file.name.lower().endswith(".csv"):
            print("File is not CSV")
            return Response(
                {"error": "Only CSV files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            print("Reading CSV file...")
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip()

            total_rows = len(df)
            print(f"Total rows in CSV: {total_rows}")

            if total_rows == 0:
                print("CSV file is empty")
                return Response(
                    {"message": "CSV file is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            batch_size = 5
            creator_id = (
                request.user.id if request.user and request.user.is_authenticated else 1
            )

            success_count = 0
            fail_count = 0
            skipped_count = 0
            skip_reason = None
            errors = []

            all_skipped = True  # Flag to check if every row was skipped

            for batch_start in range(0, total_rows, batch_size):
                batch_end = min(batch_start + batch_size, total_rows)
                batch_df = df.iloc[batch_start:batch_end].reset_index(drop=True)

                print(f"Processing batch rows {batch_start + 1} to {batch_end}")

                new_addresses = []
                new_banks = []
                new_nominees = []
                new_officials = []

                try:
                    with transaction.atomic():
                        for i, row in batch_df.iterrows():
                            row_number = batch_start + i + 1
                            print(f"Processing row {row_number}")
                            try:
                                emp_code = str(row.get("employee_code", "")).strip()
                                mobile = str(row.get("mobile_number", "")).strip()
                                name = str(row.get("name", "")).strip()
                                email = row.get("email")
                                dob = parse_custom_date(row.get("dob"))
                                gender = row.get("gender")

                                role_id = parse_int(row.get("role_id"))
                                branch_id = parse_int(row.get("branch_id"))
                                designation_id = parse_int(row.get("designation_id"))
                                department_id = parse_int(row.get("department_id"))

                                role_instance = get_instance_or_none(Role, role_id)
                                branch_instance = get_instance_or_none(
                                    TblBranch, branch_id
                                )
                                designation_instance = get_instance_or_none(
                                    TblDesignation, designation_id
                                )
                                department_instance = get_instance_or_none(
                                    TblDepartment, department_id
                                )

                                if not emp_code or not mobile or not name:
                                    fail_count += 1
                                    all_skipped = False
                                    error_msg = "Missing essential fields (employee_code, mobile_number, or name)."
                                    print(f"Row {row_number} failed: {error_msg}")
                                    errors.append(
                                        {
                                            "row": row_number,
                                            "employee_code": emp_code,
                                            "error": error_msg,
                                        }
                                    )
                                    continue

                                if (
                                    TblUser.objects.filter(
                                        employee_code=emp_code
                                    ).exists()
                                    or TblEmpBasicProfile.objects.filter(
                                        employee_code=emp_code
                                    ).exists()
                                    or TblUser.objects.filter(
                                        mobile_number=mobile
                                    ).exists()
                                ):
                                    skipped_count += 1
                                    skip_reason = (
                                        "employee_code or mobile_number already exists."
                                    )
                                    print(f"Row {row_number} skipped: {skip_reason}")
                                    continue

                                print(
                                    f"Creating TblEmpBasicProfile for row {row_number}"
                                )
                                profile = TblEmpBasicProfile.objects.create(
                                    employee_code=emp_code,
                                    name=name,
                                    email=email,
                                    mobile_number=mobile,
                                    dob=dob,
                                    gender=gender,
                                    created_by=creator_id,
                                )

                                name_part = name[:4].capitalize() if name else "User"
                                mobile_part = (
                                    mobile[-4:] if len(mobile) >= 4 else "0000"
                                )
                                user_email = (
                                    email if email else f"user_{row_number}@example.com"
                                )
                                password = f"{name_part}@{mobile_part}"

                                print(f"Creating TblUser for row {row_number}")
                                user = TblUser.objects.create(
                                    full_name=name,
                                    mobile_number=mobile,
                                    email=user_email,
                                    employee_id=profile.id,
                                    employee_code=emp_code,
                                    is_active=True,
                                    created_by=creator_id,
                                    role_id=role_instance,
                                    branch_id=branch_instance,
                                    designation_id=designation_instance,
                                    department_id=department_instance,
                                )
                                user.set_password(password)
                                user.save()

                                new_addresses.append(
                                    TblEmpAddressDetails(
                                        employee_id=profile,
                                        address=row.get("address"),
                                        city=row.get("city"),
                                        state=row.get("state"),
                                        pincode=row.get("pincode"),
                                        longitude=parse_decimal(row.get("longitude")),
                                        latitude=parse_decimal(row.get("latitude")),
                                        created_by=creator_id,
                                    )
                                )
                                new_banks.append(
                                    TblEmpBankDetails(
                                        employee_id=profile,
                                        bank_name=row.get("bank_name"),
                                        branch_name=row.get("branch_name"),
                                        account_number=row.get("account_number"),
                                        ifsc_code=row.get("ifsc_code"),
                                        created_by=creator_id,
                                    )
                                )
                                new_nominees.append(
                                    TblEmpNomineeDetails(
                                        employee_id=profile,
                                        nominee_name=clean_string(
                                            row.get("nominee_name")
                                        ),
                                        nominee_relation=clean_string(
                                            row.get("nominee_relation")
                                        ),
                                        nominee_mobile=clean_string(
                                            row.get("nominee_mobile")
                                        ),
                                        nominee_email=clean_string(
                                            row.get("nominee_email")
                                        ),
                                        nominee_address=clean_string(
                                            row.get("nominee_address")
                                        ),
                                        created_by=creator_id,
                                    )
                                )
                                new_officials.append(
                                    TblEmpOfficialInformation(
                                        employee_id=profile,
                                        reporting_to=None,
                                        employment_status=parse_int(
                                            row.get("employment_status")
                                        ),
                                        remarks=clean_string(row.get("remarks")),
                                        created_by=creator_id,
                                    )
                                )

                                success_count += 1
                                all_skipped = False
                                print(f"Row {row_number} processed successfully")

                            except Exception as row_err:
                                fail_count += 1
                                all_skipped = False
                                print(f"Error processing row {row_number}: {row_err}")
                                errors.append(
                                    {
                                        "row": row_number,
                                        "employee_code": row.get("employee_code"),
                                        "error": str(row_err),
                                    }
                                )

                        if new_addresses:
                            print(f"Bulk creating {len(new_addresses)} addresses")
                            TblEmpAddressDetails.objects.bulk_create(new_addresses)
                        if new_banks:
                            print(f"Bulk creating {len(new_banks)} bank details")
                            TblEmpBankDetails.objects.bulk_create(new_banks)
                        if new_nominees:
                            print(f"Bulk creating {len(new_nominees)} nominee details")
                            TblEmpNomineeDetails.objects.bulk_create(new_nominees)
                        if new_officials:
                            print(
                                f"Bulk creating {len(new_officials)} official info records"
                            )
                            TblEmpOfficialInformation.objects.bulk_create(new_officials)

                except IntegrityError as batch_integrity_err:
                    fail_count += batch_end - batch_start
                    print(
                        f"IntegrityError in batch {batch_start + 1}-{batch_end}: {batch_integrity_err}"
                    )
                    errors.append(
                        {
                            "batch": f"{batch_start + 1}-{batch_end}",
                            "error": f"Integrity error: {batch_integrity_err}",
                        }
                    )

                except Exception as batch_err:
                    fail_count += batch_end - batch_start
                    print(
                        f"Exception in batch {batch_start + 1}-{batch_end}: {batch_err}"
                    )
                    errors.append(
                        {
                            "batch": f"{batch_start + 1}-{batch_end}",
                            "error": str(batch_err),
                        }
                    )

            print(
                f"Import Summary: Success={success_count}, Failed={fail_count}, Skipped={skipped_count}"
            )

            if all_skipped:
                print(
                    f"All rows were skipped. Reason: {skip_reason or 'Unknown reason.'}"
                )
                return Response(
                    {
                        "message": f"⚠️ All rows were skipped. Reason: {skip_reason or 'Unknown reason.'}",
                        "imported_rows": success_count,
                        "failed_rows": fail_count,
                        "skipped_rows": skipped_count,
                        "errors": None,
                    },
                    status=status.HTTP_200_OK,
                )

            response_data = {
                "message": "✅ CSV import completed.",
                "imported_rows": success_count,
                "failed_rows": fail_count,
                "skipped_rows": skipped_count,
                "errors": errors if errors else None,
            }

            if skipped_count > 0:
                response_data["skip_reason"] = (
                    "Some rows were skipped because employee_code or mobile_number already existed."
                )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Internal server error: {str(e)}")
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
