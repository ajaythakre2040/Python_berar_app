import csv
import io
import os
from datetime import datetime
from django.conf import settings
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models.department import TblDepartment
from ems.serializers.department_serializers import TblDepartmentSerializer


class DepartmentCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # --- 1. PRE-VALIDATION ---
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not file.name.endswith(".csv"):
            return Response(
                {"error": "Only .csv files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_count = 0
        all_failed_rows = []
        internal_name_tracker = set()

        try:
            # handle BOM and decode
            decoded_file = file.read().decode("utf-8-sig")
            csv_reader = csv.DictReader(io.StringIO(decoded_file))

            # --- 2. HEADER VALIDATION ---
            required_columns = ["department_name"]
            actual_headers = [h.strip().lower() for h in (csv_reader.fieldnames or [])]

            if not any(col in actual_headers for col in required_columns):
                return Response(
                    {
                        "error": f"CSV headers missing. Required: {required_columns}",
                        "found": csv_reader.fieldnames,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --- 3. ROW PROCESSING ---
            for index, row in enumerate(csv_reader, start=2):
                # Clean data
                clean_row = {
                    k.strip().lower(): (v.strip() if v else None)
                    for k, v in row.items()
                    if k
                }
                dept_name = clean_row.get("department_name")

                try:
                    with transaction.atomic():
                        # A. Missing Check
                        if not dept_name:
                            raise ValueError("department_name is missing or empty.")

                        # B. Internal CSV Duplicate Check
                        if dept_name.lower() in internal_name_tracker:
                            raise ValueError(
                                f"Duplicate department '{dept_name}' found inside this CSV."
                            )
                        internal_name_tracker.add(dept_name.lower())

                        # C. Database Duplicate Check
                        if TblDepartment.objects.filter(
                            department_name__iexact=dept_name
                        ).exists():
                            raise ValueError(
                                f"Department '{dept_name}' already exists in the system."
                            )

                        # D. Serializer Save
                        serializer = TblDepartmentSerializer(data=clean_row)
                        if serializer.is_valid():
                            serializer.save(created_by=request.user.id)
                            success_count += 1
                        else:
                            readable_errors = " | ".join(
                                [f"{k}: {v[0]}" for k, v in serializer.errors.items()]
                            )
                            raise ValueError(readable_errors)

                except Exception as e:
                    row_err = dict(row)
                    row_err["upload_status_reason"] = str(e)
                    row_err["Row Number"] = index
                    all_failed_rows.append(row_err)

            # --- 4. ERROR REPORT GENERATION ---
            report_file_url = None
            if all_failed_rows:
                report_file_url = self.generate_error_report(
                    all_failed_rows, csv_reader.fieldnames, request
                )

            return Response(
                {
                    "message": "Processing complete",
                    "summary": {
                        "total": success_count + len(all_failed_rows),
                        "success": success_count,
                        "failed": len(all_failed_rows),
                    },
                    "report_file": report_file_url,
                },
                status=(
                    status.HTTP_200_OK
                    if not all_failed_rows
                    else status.HTTP_207_MULTI_STATUS
                ),
            )

        except Exception as fatal_e:
            return Response({"error": f"Fatal Error: {str(fatal_e)}"}, status=500)

    def generate_error_report(self, failed_rows, original_headers, request):
        log_folder = os.path.join(settings.MEDIA_ROOT, "error_logs")
        os.makedirs(log_folder, exist_ok=True)

        # Format: failed_department_28-01-2026_time_17-03-18.csv
        now = datetime.now()
        filename = f"failed_department_{now.strftime('%d-%m-%Y')}_time_{now.strftime('%H-%M-%S')}.csv"
        file_path = os.path.join(log_folder, filename)

        # Columns for error file
        fieldnames = ["Row Number", "upload_status_reason"] + list(original_headers)

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(failed_rows)

        return request.build_absolute_uri(f"{settings.MEDIA_URL}error_logs/{filename}")
