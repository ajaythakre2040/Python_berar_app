import csv
import io
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models import TblBranch
from ems.serializers.branch_serializers import TblBranchSerializer


class BranchCSVUploadView(APIView):
    # This view requires a valid user session/token
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. Double check User Object (Prevents 500 errors if middleware fails)
        if not request.user or not hasattr(request.user, "id"):
            return Response(
                {"detail": "User context missing. Please re-authenticate."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 2. File validation
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        if not file.name.endswith(".csv"):
            return Response(
                {"error": "Only CSV files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_rows = []
        error_rows = []

        try:
            # 3. Reading the file with 'utf-8-sig' to handle Excel's hidden BOM characters
            decoded_file = file.read().decode("utf-8-sig")
            csv_data = io.StringIO(decoded_file)
            csv_reader = csv.DictReader(csv_data)

            # 4. Schema check: Ensure headers match your expectations
            required_headers = ["branch_name", "branch_code"]
            if not csv_reader.fieldnames or not all(
                h in csv_reader.fieldnames for h in required_headers
            ):
                return Response(
                    {"error": f"CSV missing headers. Required: {required_headers}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 5. Iterative Processing
            for index, row in enumerate(csv_reader, start=1):
                # Strip whitespace from every cell
                clean_row = {k: (v.strip() if v else None) for k, v in row.items()}
                branch_code = clean_row.get("branch_code")

                try:
                    with transaction.atomic():
                        # Uniqueness Guard
                        if TblBranch.objects.filter(branch_code=branch_code).exists():
                            error_rows.append(
                                {
                                    "row_index": index,
                                    "branch_code": branch_code,
                                    "error": "Branch code already exists.",
                                }
                            )
                            continue

                        serializer = TblBranchSerializer(data=clean_row)
                        if serializer.is_valid():
                            # Save with the current user's integer ID
                            serializer.save(created_by=request.user.id)
                            success_rows.append(branch_code)
                        else:
                            error_rows.append(
                                {
                                    "row_index": index,
                                    "branch_code": branch_code,
                                    "error": serializer.errors,
                                }
                            )

                except IntegrityError as ie:
                    error_rows.append(
                        {"row_index": index, "error": f"Database Conflict: {str(ie)}"}
                    )
                except Exception as row_e:
                    error_rows.append(
                        {
                            "row_index": index,
                            "error": f"Unexpected Row Error: {str(row_e)}",
                        }
                    )

            # 6. Final Summary
            return Response(
                {
                    "message": "CSV Processing Task Finished",
                    "summary": {
                        "total_processed": index,
                        "success_count": len(success_rows),
                        "error_count": len(error_rows),
                    },
                    "success_list": success_rows,
                    "error_details": error_rows,
                },
                status=(
                    status.HTTP_207_MULTI_STATUS
                    if error_rows and success_rows
                    else status.HTTP_200_OK
                ),
            )

        except Exception as fatal_e:
            return Response(
                {"error": f"Critical system failure: {str(fatal_e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
