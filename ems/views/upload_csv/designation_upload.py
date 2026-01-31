import csv
import io
import os
from datetime import datetime
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from constants import PRIORITY_MAPPING
from ems.models import TblDesignation, TblDepartment


class DesignationCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        success_count = 0
        all_failed_rows = []

        # Trackers for file-level duplication
        internal_name_tracker = set()
        internal_code_tracker = set()

        try:
            decoded_file = file.read().decode("utf-8-sig")
            csv_reader = csv.DictReader(io.StringIO(decoded_file))
            rows = list(csv_reader)

            # --- 1. HEADER VALIDATION ---
            required_headers = [
                "designation_name",
                "department_name",
                "parent_designation_name",
            ]
            actual_headers = [h.strip().lower() for h in (csv_reader.fieldnames or [])]

            if not all(h in actual_headers for h in required_headers):
                return Response(
                    {
                        "error": f"Required headers missing. Needed: {required_headers}",
                        "found": csv_reader.fieldnames,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --- 2. PASS 1: VALIDATION & CREATION ---
            for index, row in enumerate(rows, start=2):
                clean_row = {
                    k.strip().lower(): (v.strip() if v else None)
                    for k, v in row.items()
                    if k
                }
                d_name = clean_row.get("designation_name")
                d_code = clean_row.get("designation_code")
                dept_name = clean_row.get("department_name")

                try:
                    with transaction.atomic():
                        # A. Mandatory Fields Check
                        if not d_name or not dept_name:
                            raise ValueError(
                                "Designation name and Department name are required."
                            )

                        # B. Designation Name: File & DB Duplicate Check
                        if d_name.lower() in internal_name_tracker:
                            raise ValueError(
                                f"Duplicate Name: '{d_name}' exists multiple times in this CSV."
                            )
                        if TblDesignation.objects.filter(
                            designation_name__iexact=d_name
                        ).exists():
                            raise ValueError(
                                f"Name Conflict: '{d_name}' already exists in database."
                            )
                        internal_name_tracker.add(d_name.lower())

                        # C. Designation Code: File & DB Duplicate Check (Model: unique=True)
                        if d_code:
                            if d_code.lower() in internal_code_tracker:
                                raise ValueError(
                                    f"Duplicate Code: '{d_code}' exists multiple times in this CSV."
                                )
                            if TblDesignation.objects.filter(
                                designation_code__iexact=d_code
                            ).exists():
                                raise ValueError(
                                    f"Code Conflict: Code '{d_code}' is already assigned in database."
                                )
                            internal_code_tracker.add(d_code.lower())

                        # D. Department Lookup
                        dept_obj = TblDepartment.objects.filter(
                            department_name__iexact=dept_name
                        ).first()
                        if not dept_obj:
                            raise ValueError(
                                f"Department '{dept_name}' not found in system."
                            )

                        # E. Priority Mapping
                        p_str = (
                            clean_row.get("designation_priority") or "Medium"
                        ).capitalize()
                        priority_val = PRIORITY_MAPPING.get(p_str, 1)

                        # F. Initial Create (Parent ID = 0)
                        TblDesignation.objects.create(
                            designation_name=d_name,
                            designation_code=d_code,
                            department=dept_obj,
                            designation_priority=priority_val,
                            parent_designation_id=0,
                            created_by=request.user.id,
                        )
                        success_count += 1

                except Exception as e:
                    row_err = dict(row)
                    row_err["Row Number"] = index
                    row_err["upload_status_reason"] = str(e)
                    all_failed_rows.append(row_err)

            # --- 3. PASS 2: HIERARCHY LINKING ---
            for row in rows:
                clean_row = {
                    k.strip().lower(): (v.strip() if v else None)
                    for k, v in row.items()
                    if k
                }
                d_name = clean_row.get("designation_name")
                parent_name = clean_row.get("parent_designation_name")

                # "0" logic handle: Agar parent valid name hai tabhi link karein
                if (
                    d_name
                    and parent_name
                    and parent_name not in ["0", "None", "null", ""]
                ):
                    parent_obj = TblDesignation.objects.filter(
                        designation_name__iexact=parent_name
                    ).first()
                    if parent_obj:
                        TblDesignation.objects.filter(
                            designation_name__iexact=d_name
                        ).update(parent_designation_id=parent_obj.id)

            # --- 4. ERROR REPORT GENERATION ---
            report_url = None
            if all_failed_rows:
                report_url = self.generate_error_report(
                    all_failed_rows, csv_reader.fieldnames, request
                )

            return Response(
                {
                    "message": "Processing Complete",
                    "summary": {
                        "total": len(rows),
                        "success": success_count,
                        "failed": len(all_failed_rows),
                    },
                    "report_file": report_url,
                },
                status=(
                    status.HTTP_200_OK
                    if not all_failed_rows
                    else status.HTTP_207_MULTI_STATUS
                ),
            )

        except Exception as fatal:
            return Response({"error": f"Fatal System Error: {str(fatal)}"}, status=500)

    def generate_error_report(self, failed_rows, original_headers, request):
        log_dir = os.path.join(settings.MEDIA_ROOT, "error_logs")
        os.makedirs(log_dir, exist_ok=True)
        now = datetime.now()
        # Filename Format: failed_designations_28-01-2026_time_18-30-00.csv
        filename = f"failed_designations_{now.strftime('%d-%m-%Y')}_time_{now.strftime('%H-%M-%S')}.csv"
        path = os.path.join(log_dir, filename)

        fieldnames = ["Row Number", "upload_status_reason"] + list(original_headers)
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(failed_rows)
        return request.build_absolute_uri(settings.MEDIA_URL + "error_logs/" + filename)
