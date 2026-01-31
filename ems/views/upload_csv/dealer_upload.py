import csv
import io
import os
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

from ems.models import Dealer, TblBranch
from ems.serializers.dealer_serializer import DealerSerializer


class DealerCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. Initial File Validation
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not file.name.endswith(".csv"):
            return Response(
                {"error": "File must be in .csv format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_count = 0
        failed_rows = []
        internal_code_tracker = set()  # To catch duplicates inside the CSV file

        try:
            # 2. Stream Reading (Memory Efficient for large files)
            # utf-8-sig handles the Byte Order Mark (BOM) from Excel CSVs
            csv_file = io.TextIOWrapper(file.file, encoding="utf-8-sig")
            reader = csv.DictReader(csv_file)

            # 3. Dynamic Header Validation
            # Clean headers: remove spaces and convert to lowercase
            raw_headers = reader.fieldnames if reader.fieldnames else []
            header_map = {h.strip().lower(): h for h in raw_headers}

            required_fields = [
                "branch",
                "code",
                "name",
                "state",
                "district",
                "city",
                "pin_code",
                "address_1",
                "mobile_number",
                "email",
            ]
            missing_fields = [f for f in required_fields if f not in header_map]

            if missing_fields:
                return Response(
                    {
                        "error": "Invalid CSV Structure",
                        "missing_columns": missing_fields,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 4. Process Each Row
            for index, row in enumerate(reader, start=2):  # Row 2 matches Excel row 2
                # Clean row data (strip spaces)
                clean_data = {
                    k.strip().lower(): (v.strip() if v else None)
                    for k, v in row.items()
                }

                # Extract clean values using the lowercase map
                row_code = clean_data.get("code")
                branch_name = clean_data.get("branch")

                try:
                    with transaction.atomic():
                        # --- Logic A: Row Integrity ---
                        if not row_code or not branch_name:
                            raise ValueError(
                                "Code and Branch name are mandatory fields."
                            )

                        # --- Logic B: Internal Duplicate Check (CSV Level) ---
                        if row_code in internal_code_tracker:
                            raise ValueError(
                                f"Duplicate Code '{row_code}' found within this CSV file."
                            )
                        internal_code_tracker.add(row_code)

                        # --- Logic C: Database Duplicate Check ---
                        if Dealer.objects.filter(code=row_code).exists():
                            raise ValueError(
                                f"Dealer with code '{row_code}' already exists in the system."
                            )

                        # --- Logic D: Relationship Validation ---
                        branch_obj = TblBranch.objects.filter(
                            branch_name__iexact=branch_name
                        ).first()
                        if not branch_obj:
                            raise ValueError(
                                f"Branch '{branch_name}' does not exist in the database."
                            )

                        # --- Logic E: Data Format Validation (Serializer) ---
                        # Inject the branch ID into data for the serializer
                        serializer_data = {
                            k: v for k, v in row.items()
                        }  # Use original row for serializer
                        serializer_data["branch_id"] = branch_obj.branch_id

                        serializer = DealerSerializer(data=serializer_data)
                        if serializer.is_valid():
                            serializer.save(created_by=request.user.id)
                            success_count += 1
                        else:
                            # Convert serializer errors into a readable string
                            err_msg = " | ".join(
                                [
                                    f"{k.title()}: {v[0]}"
                                    for k, v in serializer.errors.items()
                                ]
                            )
                            raise ValueError(err_msg)

                except Exception as e:
                    # Append error info to the row and add to failed list
                    row["Failure Reason"] = str(e)
                    row["Row Number"] = index
                    failed_rows.append(row)

            # 5. Handle Error File Generation
            error_file_url = None
            if failed_rows:
                error_file_url = self.generate_error_report(failed_rows, request)

            return Response(
                {
                    "message": "Upload process completed.",
                    "summary": {
                        "total_rows_processed": success_count + len(failed_rows),
                        "successful_inserts": success_count,
                        "failed_inserts": len(failed_rows),
                    },
                    "report_file": error_file_url,
                    # "preview_errors": [
                    #     {"row": r["Row Number"], "reason": r["Failure Reason"]}
                    #     for r in failed_rows[:5]
                    # ],
                },
                status=status.HTTP_200_OK,
            )

        except Exception as fatal_e:
            return Response(
                {"error": f"Critical system error: {str(fatal_e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def generate_error_report(self, failed_rows, request):
        """Helper to create and save a CSV of failed records."""
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        now = datetime.now()
        filename = f"failed_dealers_{now.strftime('%d-%m-%Y')}_time_{now.strftime('%H-%M-%S')}.csv"
        filepath = os.path.join("error_logs/", filename)
        full_path = os.path.join(settings.MEDIA_ROOT, filepath)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, mode="w", newline="", encoding="utf-8") as f:
            if failed_rows:
                # Ensure 'Row Number' and 'Failure Reason' appear first in columns
                headers = ["Row Number", "Failure Reason"] + [
                    k
                    for k in failed_rows[0].keys()
                    if k not in ["Row Number", "Failure Reason"]
                ]
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(failed_rows)

        return request.build_absolute_uri(settings.MEDIA_URL + filepath)
