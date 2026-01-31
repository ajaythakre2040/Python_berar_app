import csv
import io
import os
import re
from datetime import datetime
from django.conf import settings
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models import TblBranch
from ems.serializers.branch_serializers import TblBranchSerializer


class BranchCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        success_count = 0
        error_count = 0
        all_failed_rows = []
        internal_code_tracker = set()

        try:
            decoded_file = file.read().decode("utf-8-sig")
            csv_reader = csv.DictReader(io.StringIO(decoded_file))

            # --- 1. Required Headers Check ---
            # Aapke model ke hisab se mandatory fields
            required_headers = ["branch_name", "branch_code"]
            actual_headers = [h.strip().lower() for h in (csv_reader.fieldnames or [])]
            missing_headers = [h for h in required_headers if h not in actual_headers]

            if missing_headers:
                return Response(
                    {
                        "error": "CSV columns missing",
                        "missing": missing_headers,
                        "tip": f"Please ensure these headers exist: {', '.join(required_headers)}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --- 2. Row Processing ---
            for index, row in enumerate(csv_reader, start=2):
                clean_row = {
                    k.strip().lower(): (v.strip() if v else None)
                    for k, v in row.items()
                }

                try:
                    with transaction.atomic():
                        branch_code = clean_row.get("branch_code")

                        # A. Missing Data Check
                        if not branch_code:
                            raise ValueError("branch_code is required but found empty.")

                        # B. Internal CSV Duplicate Check
                        if branch_code in internal_code_tracker:
                            raise ValueError(
                                f"Duplicate branch_code '{branch_code}' found inside this CSV file."
                            )
                        internal_code_tracker.add(branch_code)

                        # C. Database Duplicate Check
                        if TblBranch.objects.filter(branch_code=branch_code).exists():
                            raise ValueError(
                                f"Branch with code '{branch_code}' already exists in database."
                            )

                        # D. Email & Mobile Format Validation
                        email = clean_row.get("email")
                        if email and email.lower() not in ["null", "nan", "none"]:
                            try:
                                validate_email(email)
                            except ValidationError:
                                raise ValueError(f"Invalid email format: {email}")

                        # E. Serializer Validation & Save
                        serializer = TblBranchSerializer(data=clean_row)
                        if serializer.is_valid():
                            serializer.save(created_by=request.user.id)
                            success_count += 1
                        else:
                            # Capturing Serializer/Model errors (like max_length)
                            err_msg = " | ".join(
                                [f"{k}: {v[0]}" for k, v in serializer.errors.items()]
                            )
                            raise ValueError(err_msg)

                except Exception as e:
                    error_count += 1
                    row_err = dict(row)
                    row_err["upload_status_reason"] = str(e)
                    all_failed_rows.append(row_err)

            # --- 3. Generate Error Report with Specific Filename ---
            report_url = None
            if all_failed_rows:
                report_url = self.generate_error_report(
                    all_failed_rows, csv_reader.fieldnames, request
                )

            return Response(
                {
                    "message": "Processing finished",
                    "summary": {
                        "created": success_count,
                        "failed_or_skipped": error_count,
                        "total": success_count + error_count,
                    },
                    "report_file": report_url,
                },
                status=(
                    status.HTTP_200_OK
                    if not all_failed_rows
                    else status.HTTP_207_MULTI_STATUS
                ),
            )

        except Exception as fatal_e:
            return Response(
                {"error": f"Fatal System Error: {str(fatal_e)}"}, status=500
            )

    def generate_error_report(self, failed_rows, original_headers, request):
        log_folder = os.path.join(settings.MEDIA_ROOT, "error_logs")
        os.makedirs(log_folder, exist_ok=True)

        # Aapka Required Format: failed_branch_28-01-2026_time_17-03-18.csv
        now = datetime.now()
        filename = f"failed_branch_{now.strftime('%d-%m-%Y')}_time_{now.strftime('%H-%M-%S')}.csv"
        file_path = os.path.join(log_folder, filename)

        # Fieldnames setup (Reason column first)
        fieldnames = ["upload_status_reason"] + list(original_headers)

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(failed_rows)

        return request.build_absolute_uri(f"{settings.MEDIA_URL}error_logs/{filename}")
