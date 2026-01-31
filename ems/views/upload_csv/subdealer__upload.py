import csv
from datetime import datetime
import io
import os
import re
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models import SubDealer, Dealer, TblBranch
from ems.serializers.subdealer_serializer import SubDealerSerializer


class SubDealerCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not file.name.endswith(".csv"):
            return Response(
                {"error": "Only CSV files (.csv) are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_count = 0
        failed_rows = []
        internal_code_tracker = set()

        try:
            # handle BOM and decode
            decoded_file = file.read().decode("utf-8-sig")
            csv_data = io.StringIO(decoded_file)
            csv_reader = csv.DictReader(csv_data)

            # 1. Validation: Required Headers
            required_headers = [
                "code",
                "name",
                "dealer_name",
                "branch_name",
                "mobile_number",
                "address_1",
                "email",
                "district",
                "pin_code",
                "state",
                "city",
            ]

            actual_headers = [h.strip().lower() for h in (csv_reader.fieldnames or [])]
            missing_headers = [h for h in required_headers if h not in actual_headers]

            if missing_headers:
                return Response(
                    {
                        "error": "CSV headers missing or incorrect",
                        "missing_columns": missing_headers,
                        "tip": f"Headers must include: {', '.join(required_headers)}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 2. Validation: Row Processing
            for index, row in enumerate(csv_reader, start=2):
                # Clean keys and values
                clean_row = {
                    k.strip().lower(): (v.strip() if v else None)
                    for k, v in row.items()
                }

                try:
                    with transaction.atomic():
                        subdealer_code = clean_row.get("code")

                        # --- Basic Field Validations ---
                        if not subdealer_code:
                            raise ValueError("Sub-dealer code is missing.")

                        # File-level duplicate check
                        if subdealer_code in internal_code_tracker:
                            raise ValueError(
                                f"Duplicate code '{subdealer_code}' found within this CSV file."
                            )
                        internal_code_tracker.add(subdealer_code)

                        # Database-level duplicate check
                        if SubDealer.objects.filter(code=subdealer_code).exists():
                            raise ValueError(
                                f"Sub-dealer with code '{subdealer_code}' is already registered."
                            )

                        # Email format check
                        email = clean_row.get("email")
                        if email:
                            try:
                                validate_email(email)
                            except ValidationError:
                                raise ValueError(f"Invalid email format: {email}")

                        # Mobile number check (Basic 10 digits)
                        mobile = clean_row.get("mobile_number")
                        if mobile and not re.match(r"^\d{10}$", mobile):
                            raise ValueError(
                                f"Invalid mobile number: {mobile}. Must be 10 digits."
                            )

                        # --- Relationship Lookups ---
                        d_name = clean_row.get("dealer_name")
                        dealer_obj = Dealer.objects.filter(name__iexact=d_name).first()
                        if not dealer_obj:
                            raise ValueError(
                                f"Dealer '{d_name}' does not exist in the database."
                            )

                        b_name = clean_row.get("branch_name")
                        branch_obj = TblBranch.objects.filter(
                            branch_name__iexact=b_name
                        ).first()
                        if not branch_obj:
                            raise ValueError(f"Branch '{b_name}' does not exist.")

                        # --- Serialization and Saving ---
                        data_to_save = {
                            k: v.strip() if v else v for k, v in row.items()
                        }
                        data_to_save["dealer_id"] = dealer_obj.id
                        data_to_save["branch_id"] = str(branch_obj.branch_id)

                        serializer = SubDealerSerializer(data=data_to_save)
                        if serializer.is_valid():
                            serializer.save(created_by=request.user.id)
                            success_count += 1
                        else:
                            error_text = " | ".join(
                                [f"{k}: {v[0]}" for k, v in serializer.errors.items()]
                            )
                            raise ValueError(error_text)

                except Exception as e:
                    row_err = dict(row)
                    row_err["Row Number"] = index
                    row_err["Failure Reason"] = str(e)
                    failed_rows.append(row_err)

            # 3. Final Report & Response
            error_file_url = (
                self.generate_error_report(failed_rows, request)
                if failed_rows
                else None
            )

            return Response(
                {
                    "message": "Process completed.",
                    "total_records": success_count + len(failed_rows),
                    "success_count": success_count,
                    "error_count": len(failed_rows),
                    "report_file": error_file_url,
                    "recent_errors": [
                        {"row": r["Row Number"], "error": r["Failure Reason"]}
                        for r in failed_rows[:10]
                    ],
                },
                status=(
                    status.HTTP_200_OK
                    if not failed_rows
                    else status.HTTP_207_MULTI_STATUS
                ),
            )

        except Exception as fatal_e:
            return Response(
                {"error": f"Internal System Error: {str(fatal_e)}"}, status=500
            )

    def generate_error_report(self, failed_rows, request):
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        now = datetime.now()
        error_filename = f"failed_subdealer_{now.strftime('%d-%m-%Y')}_time_{now.strftime('%H-%M-%S')}.csv"
        error_folder = os.path.join(settings.MEDIA_ROOT, "error_logs")
        os.makedirs(error_folder, exist_ok=True)
        path = os.path.join(error_folder, error_filename)

        with open(path, mode="w", newline="", encoding="utf-8") as f:
            # Make "Row Number" and "Failure Reason" the first two columns
            base_fields = ["Row Number", "Failure Reason"]
            other_fields = [k for k in failed_rows[0].keys() if k not in base_fields]
            writer = csv.DictWriter(f, fieldnames=base_fields + other_fields)

            writer.writeheader()
            writer.writerows(failed_rows)

        return request.build_absolute_uri(
            settings.MEDIA_URL + "error_logs/" + error_filename
        )
