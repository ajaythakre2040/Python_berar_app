import csv
import io
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models import TblDesignation, TblDepartment
from ems.serializers.designation_serializers import TblDesignationSerializer


class DesignationCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. Check if file is provided
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        # 2. Extension Check
        if not file.name.endswith(".csv"):
            return Response(
                {"error": "Only .csv files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_rows = []
        error_rows = []

        try:
            # 3. Handle Encoding (Excel BOM support)
            decoded_file = file.read().decode("utf-8-sig")
            csv_data = io.StringIO(decoded_file)
            csv_reader = csv.DictReader(csv_data)

            # 4. Mandatory Headers Check
            # Note: CSV me header 'department_id' hona chahiye
            required_headers = ["designation_name", "department_id"]
            if not csv_reader.fieldnames or not all(
                h in csv_reader.fieldnames for h in required_headers
            ):
                return Response(
                    {"error": f"CSV missing required headers: {required_headers}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 5. Process Rows
            for index, row in enumerate(csv_reader, start=1):
                clean_data = {k: (v.strip() if v else None) for k, v in row.items()}
                designation_name = clean_data.get("designation_name")

                try:
                    with transaction.atomic():
                        serializer = TblDesignationSerializer(data=clean_data)

                        if serializer.is_valid():
                            # Save with created_by as integer ID
                            serializer.save(created_by=request.user.id)
                            success_rows.append(designation_name)
                        else:
                            error_rows.append(
                                {
                                    "row_index": index,
                                    "name": designation_name or "Unknown",
                                    "errors": serializer.errors,
                                }
                            )

                except IntegrityError as ie:
                    error_rows.append(
                        {"row_index": index, "errors": f"Database Conflict: {str(ie)}"}
                    )
                except Exception as e:
                    error_rows.append(
                        {
                            "row_index": index,
                            "errors": f"System error on row {index}: {str(e)}",
                        }
                    )

            # 6. Response Logic
            res_status = status.HTTP_200_OK
            if error_rows and success_rows:
                res_status = status.HTTP_207_MULTI_STATUS
            elif error_rows and not success_rows:
                res_status = status.HTTP_400_BAD_REQUEST

            return Response(
                {
                    "message": "CSV Processing Task Finished",
                    "summary": {
                        "total": len(success_rows) + len(error_rows),
                        "success": len(success_rows),
                        "failed": len(error_rows),
                    },
                    "success_data": success_rows,
                    "error_details": error_rows,
                },
                status=res_status,
            )

        except Exception as fatal_e:
            return Response(
                {"error": f"Fatal error: {str(fatal_e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
